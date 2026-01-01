#!/usr/bin/env python3
"""
MCP Server with Pydantic Models - SSE HTTP Transport
Provides type-safe tool inputs and structured outputs over HTTP with SSE
"""

import logging
from typing import Any, Optional
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, ConfigDict
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# PYDANTIC INPUT MODELS - Type-safe tool inputs

class CalculateInput(BaseModel):
    """Input model for calculation tool"""
    operation: str = Field(..., description="Arithmetic operation", pattern="^(add|subtract|multiply|divide)$")
    a: float = Field(..., description="First number")
    b: float = Field(..., description="Second number")
    
    @field_validator('b')
    @classmethod
    def validate_division(cls, v, info):
        """Prevent division by zero"""
        if info.data.get('operation') == 'divide' and v == 0:
            raise ValueError("Cannot divide by zero")
        return v


class WeatherInput(BaseModel):
    """Input model for weather tool"""
    city: str = Field(..., description="City name", min_length=1, max_length=100)
    
    @field_validator('city')
    @classmethod
    def validate_city(cls, v):
        """Sanitize city name"""
        return v.strip()


class NoteInput(BaseModel):
    """Input model for saving notes"""
    title: str = Field(..., description="Note title", min_length=1, max_length=100)
    content: str = Field(..., description="Note content", min_length=1)
    tags: Optional[list[str]] = Field(default=None, description="Optional tags for categorization")
    
    @field_validator('title')
    @classmethod
    def sanitize_title(cls, v):
        """Sanitize title for safe filename"""
        # Remove special characters
        safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ ")
        sanitized = "".join(c for c in v if c in safe_chars).strip()
        if not sanitized:
            raise ValueError("Title must contain at least one alphanumeric character")
        return sanitized


class TemperatureInput(BaseModel):
    """Input model for temperature conversion"""
    temperature_fahrenheit: float = Field(..., description="Temperature in Fahrenheit")
    
    @field_validator('temperature_fahrenheit')
    @classmethod
    def validate_temperature(cls, v):
        """Validate temperature is within reasonable bounds"""
        if v < -459.67:  # Absolute zero in Fahrenheit
            raise ValueError("Temperature cannot be below absolute zero (-459.67°F)")
        return v


class FileReadInput(BaseModel):
    """Input model for reading files"""
    filename: str = Field(..., description="Name of file to read", min_length=1)
    
    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        """Ensure filename is safe (no path traversal)"""
        # Only allow basename, no path components
        safe_filename = Path(v).name
        if not safe_filename or safe_filename != v:
            raise ValueError("Invalid filename - path traversal not allowed")
        return safe_filename


class TimeInput(BaseModel):
    """Input model for getting time"""
    format: str = Field(
        default="iso",
        description="Time format",
        pattern="^(iso|human|unix)$"
    )


# PYDANTIC OUTPUT MODELS - Structured responses

class CalculateOutput(BaseModel):
    """Structured output for calculations"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "operation": "multiply",
            "operand_a": 5,
            "operand_b": 3,
            "result": 15,
            "formatted": "5 multiply 3 = 15"
        }
    })
    
    operation: str
    operand_a: float
    operand_b: float
    result: float
    formatted: str
    timestamp: datetime = Field(default_factory=datetime.now)


class WeatherOutput(BaseModel):
    """Structured output for weather data"""
    city: str
    temperature: str
    temperature_celsius: Optional[float] = None
    condition: str
    humidity: str
    wind: str
    timestamp: datetime = Field(default_factory=datetime.now)


class NoteOutput(BaseModel):
    """Structured output for note operations"""
    filename: str
    title: str
    content_length: int
    tags: Optional[list[str]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    success: bool = True
    message: str


class TemperatureOutput(BaseModel):
    """Structured output for temperature conversion"""
    fahrenheit: float
    celsius: float
    formatted: str
    timestamp: datetime = Field(default_factory=datetime.now)


class FileReadOutput(BaseModel):
    """Structured output for file reading"""
    filename: str
    content: str
    size_bytes: int
    lines: int
    success: bool = True


class TimeOutput(BaseModel):
    """Structured output for time requests"""
    timestamp: datetime
    formatted: str
    format_type: str
    timezone: str = "UTC"


class ErrorOutput(BaseModel):
    """Structured error response"""
    success: bool = False
    error_type: str
    error_message: str
    timestamp: datetime = Field(default_factory=datetime.now)
