#!/usr/bin/env python3
"""
Test country detection with capital city overrides
"""
from utils import get_country_from_coordinates

test_cases = [
    (59.9139, 10.7522, 'NO', 'Oslo'),
    (59.3293, 18.0686, 'SE', 'Stockholm'),
    (55.6761, 12.5683, 'DK', 'Copenhagen'),
    (60.1699, 24.9384, 'FI', 'Helsinki'),
    (60.3913, 5.3221, 'NO', 'Bergen'),
    (57.7089, 11.9746, 'SE', 'Gothenburg'),
]

print('Testing get_country_from_coordinates() with capital city overrides:\n')
all_passed = True
for lat, lon, expected, city in test_cases:
    result = get_country_from_coordinates(lat, lon)
    status = '✓' if result == expected else '✗'
    if result != expected:
        all_passed = False
    print(f'{status} {city:15} ({lat:.4f}, {lon:.4f}): {result:2} - Expected: {expected}')

print(f'\n{"SUCCESS" if all_passed else "FAILED"}: {"All tests passed!" if all_passed else "Some tests failed"}')
