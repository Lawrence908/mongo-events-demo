"""
Google Maps Geocoding Service

This module provides geocoding and reverse geocoding functionality using the Google Maps API.
It handles address-to-coordinates conversion and coordinates-to-address conversion.
"""

import os
import requests
from typing import Optional, Dict, Any, Tuple
from urllib.parse import quote_plus

from .models import EventAddress, EventLocation


class GeocodingError(Exception):
    """Custom exception for geocoding-related errors"""
    pass


class GeocodingService:
    """Service for Google Maps geocoding operations"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY", "")
        self.geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.directions_url = "https://www.google.com/maps/dir/?api=1"
        
        if not self.api_key:
            raise GeocodingError("Google Maps API key is required")
    
    def geocode_address(self, address: EventAddress) -> Tuple[float, float]:
        """
        Convert address to coordinates using Google Maps Geocoding API
        
        Args:
            address: EventAddress object with street, city, state, zip, country
            
        Returns:
            Tuple of (longitude, latitude)
            
        Raises:
            GeocodingError: If geocoding fails
        """
        try:
            # Format address string
            address_str = f"{address.street}, {address.city}, {address.state} {address.zip}, {address.country}"
            
            params = {
                "address": address_str,
                "key": self.api_key
            }
            
            response = requests.get(self.geocoding_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "OK":
                raise GeocodingError(f"Geocoding failed: {data.get('status', 'Unknown error')}")
            
            results = data.get("results", [])
            if not results:
                raise GeocodingError("No results found for the given address")
            
            # Get the first result
            location = results[0]["geometry"]["location"]
            longitude = location["lng"]
            latitude = location["lat"]
            
            return longitude, latitude
            
        except requests.RequestException as e:
            raise GeocodingError(f"Network error during geocoding: {str(e)}")
        except (KeyError, ValueError) as e:
            raise GeocodingError(f"Invalid response format: {str(e)}")
    
    def reverse_geocode(self, longitude: float, latitude: float) -> EventAddress:
        """
        Convert coordinates to address using Google Maps Geocoding API
        
        Args:
            longitude: Longitude coordinate
            latitude: Latitude coordinate
            
        Returns:
            EventAddress object with parsed address components
            
        Raises:
            GeocodingError: If reverse geocoding fails
        """
        try:
            params = {
                "latlng": f"{latitude},{longitude}",
                "key": self.api_key
            }
            
            response = requests.get(self.geocoding_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "OK":
                raise GeocodingError(f"Reverse geocoding failed: {data.get('status', 'Unknown error')}")
            
            results = data.get("results", [])
            if not results:
                raise GeocodingError("No results found for the given coordinates")
            
            # Parse address components from the first result
            address_components = results[0].get("address_components", [])
            
            # Initialize address components
            street_number = ""
            route = ""
            city = ""
            state = ""
            zip_code = ""
            country = ""
            
            for component in address_components:
                types = component.get("types", [])
                long_name = component.get("long_name", "")
                
                if "street_number" in types:
                    street_number = long_name
                elif "route" in types:
                    route = long_name
                elif "locality" in types or "administrative_area_level_2" in types:
                    city = long_name
                elif "administrative_area_level_1" in types:
                    state = long_name
                elif "postal_code" in types:
                    zip_code = long_name
                elif "country" in types:
                    country = long_name
            
            # Combine street number and route
            street = f"{street_number} {route}".strip()
            
            # Validate that we have the minimum required components
            if not all([street, city, state, country]):
                raise GeocodingError("Could not parse complete address from coordinates")
            
            return EventAddress(
                street=street,
                city=city,
                state=state,
                zip=zip_code or "00000",  # Default if no postal code
                country=country
            )
            
        except requests.RequestException as e:
            raise GeocodingError(f"Network error during reverse geocoding: {str(e)}")
        except (KeyError, ValueError) as e:
            raise GeocodingError(f"Invalid response format: {str(e)}")
    
    def generate_directions_url(self, destination_address: Optional[str] = None, 
                              destination_coords: Optional[Tuple[float, float]] = None) -> str:
        """
        Generate Google Maps directions URL
        
        Args:
            destination_address: Full address string
            destination_coords: Tuple of (longitude, latitude)
            
        Returns:
            Google Maps directions URL
            
        Raises:
            GeocodingError: If neither address nor coordinates are provided
        """
        if destination_address:
            # URL encode the address
            encoded_address = quote_plus(destination_address)
            return f"{self.directions_url}&destination={encoded_address}"
        elif destination_coords:
            lng, lat = destination_coords
            return f"{self.directions_url}&destination={lat},{lng}"
        else:
            raise GeocodingError("Either destination_address or destination_coords must be provided")
    
    def validate_and_geocode_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate event data and ensure coordinates are available
        
        This method handles the bidirectional conversion:
        - If address is provided but no coordinates, geocode the address
        - If coordinates are provided but no address, reverse geocode to get address
        - Generate directions URL if possible
        
        Args:
            event_data: Event data dictionary
            
        Returns:
            Updated event data with coordinates, address, and directions_url
            
        Raises:
            GeocodingError: If geocoding fails
        """
        updated_data = event_data.copy()
        
        # Check if we have location coordinates
        location = updated_data.get("location", {})
        coordinates = location.get("coordinates") if location else None
        
        # Check if we have address
        address = updated_data.get("address")
        
        # Case 1: Address provided but no coordinates - geocode
        if address and not coordinates:
            try:
                address_obj = EventAddress(**address)
                lng, lat = self.geocode_address(address_obj)
                updated_data["location"] = {
                    "type": "Point",
                    "coordinates": [lng, lat]
                }
                coordinates = [lng, lat]
            except Exception as e:
                raise GeocodingError(f"Failed to geocode address: {str(e)}")
        
        # Case 2: Coordinates provided but no address - reverse geocode
        elif coordinates and not address:
            try:
                lng, lat = coordinates
                address_obj = self.reverse_geocode(lng, lat)
                updated_data["address"] = address_obj.model_dump()
            except Exception as e:
                # Don't fail the entire operation if reverse geocoding fails
                # Just log the error and continue without address
                print(f"Warning: Failed to reverse geocode coordinates: {str(e)}")
        
        # Case 3: Neither address nor coordinates - this is an error
        elif not address and not coordinates:
            raise GeocodingError("Either address or coordinates must be provided")
        
        # Generate directions URL if we have coordinates
        if coordinates:
            try:
                lng, lat = coordinates
                directions_url = self.generate_directions_url(destination_coords=(lng, lat))
                updated_data["directions_url"] = directions_url
            except Exception as e:
                # Don't fail if directions URL generation fails
                print(f"Warning: Failed to generate directions URL: {str(e)}")
        
        return updated_data


def get_geocoding_service() -> GeocodingService:
    """Get a configured geocoding service instance"""
    return GeocodingService()
