#!/usr/bin/env python3
"""
Test script to analyze compartment hierarchy data structure.
"""

import asyncio
import sys
import os

# Add the backend app to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.cloud_service import OCIService

async def check_compartments():
    oci_service = OCIService()
    compartments = await oci_service.get_compartments()
    
    print('COMPARTMENT DATA ANALYSIS:')
    print('=' * 50)
    for i, comp in enumerate(compartments, 1):
        print(f'{i}. NAME: {comp["name"]}')
        print(f'   ID: {comp["id"]}')
        print(f'   PARENT_ID: {comp.get("compartment_id", "None")}')
        print(f'   STATE: {comp.get("lifecycle_state", "Unknown")}')
        print()
    
    # Check hierarchy relationships
    print('HIERARCHY ANALYSIS:')
    print('=' * 30)
    root_count = 0
    for comp in compartments:
        parent_id = comp.get('compartment_id')
        if not parent_id or comp['name'].lower() in ['root', 'tenancy'] or 'root' in comp['name'].lower():
            root_count += 1
            print(f'ROOT: {comp["name"]} (no parent)')
        else:
            parent = next((c for c in compartments if c['id'] == parent_id), None)
            parent_name = parent['name'] if parent else 'UNKNOWN PARENT'
            print(f'CHILD: {comp["name"]} -> parent: {parent_name}')
    
    print(f'\nTotal compartments: {len(compartments)}')
    print(f'Root compartments: {root_count}')
    
    # Test hierarchy building logic (same as frontend)
    print('\nTESTING HIERARCHY BUILDING LOGIC:')
    print('=' * 40)
    
    def build_hierarchy(compartments):
        if not compartments or len(compartments) == 0:
            return []

        hierarchy = []
        
        # Find root compartments
        roots = [c for c in compartments if 
                not c.get('compartment_id') or 
                c['name'].lower().find('root') != -1 or
                c['name'].lower().find('tenancy') != -1]
        
        def add_to_hierarchy(comp, level=0):
            # Find children for this compartment
            children = [c for c in compartments if c.get('compartment_id') == comp['id']]
            has_children = len(children) > 0
            
            hierarchy.append({**comp, 'level': level, 'hasChildren': has_children})
            
            # Recursively add children, sorted by name
            children.sort(key=lambda x: x['name'])
            for child in children:
                add_to_hierarchy(child, level + 1)
        
        # Start with root compartments, sorted by name
        roots.sort(key=lambda x: x['name'])
        for root in roots:
            add_to_hierarchy(root, 0)
        
        # Add any orphaned compartments at level 0
        processed_ids = {h['id'] for h in hierarchy}
        orphaned = [comp for comp in compartments if comp['id'] not in processed_ids]
        orphaned.sort(key=lambda x: x['name'])
        
        for comp in orphaned:
            add_to_hierarchy(comp, 0)
        
        return hierarchy
    
    hierarchical_compartments = build_hierarchy(compartments)
    
    print('HIERARCHICAL DISPLAY:')
    for comp in hierarchical_compartments:
        indent = '  ' * comp['level']
        prefix = '└─ ' if comp['level'] > 0 else ''
        status_icon = '✓' if comp.get('lifecycle_state') == 'ACTIVE' else '⚠'
        child_indicator = ' 📁' if comp['hasChildren'] else ''
        
        print(f"{indent}{prefix}{status_icon} {comp['name']}{child_indicator}")

if __name__ == "__main__":
    asyncio.run(check_compartments()) 