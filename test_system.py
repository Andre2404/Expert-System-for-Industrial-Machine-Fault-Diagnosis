"""
Test script untuk Sistem Pakar
"""

from inference_engine import InferenceEngine
import json

def test_diagnosis():
    """Test diagnosis dengan berbagai gejala"""
    
    print("=" * 60)
    print("TEST SISTEM PAKAR KERUSAKAN MESIN INDUSTRI")
    print("=" * 60)
    print()
    
    # Initialize engine
    engine = InferenceEngine('knowledge_base.json', 'diagnosis_data.json')
    
    # Test cases
    test_cases = [
        {
            'name': 'Test Case 1: Unbalance',
            'symptoms': ['Q2', 'Q8'],
            'expected': 'Unbalance'
        },
        {
            'name': 'Test Case 2: Misalignment',
            'symptoms': ['Q1', 'Q2', 'Q3', 'Q6', 'Q7', 'Q13'],
            'expected': 'Misalignment'
        },
        {
            'name': 'Test Case 3: Mechanical Looseness',
            'symptoms': ['Q2', 'Q4', 'Q9'],
            'expected': 'Mechanical_Looseness'
        },
        {
            'name': 'Test Case 4: Bent Shaft',
            'symptoms': ['Q1', 'Q3'],
            'expected': 'Bent_Shaft'
        },
        {
            'name': 'Test Case 5: Bearing Defect',
            'symptoms': ['Q10', 'Q11', 'Q12'],
            'expected': 'Bearing_Defect'
        }
    ]
    
    # Run tests
    for i, test in enumerate(test_cases, 1):
        print(f"\n{test['name']}")
        print("-" * 60)
        
        diagnoses, reasoning = engine.forward_chaining(test['symptoms'])
        
        if diagnoses:
            top_diagnosis = diagnoses[0]
            print(f"Gejala: {', '.join(test['symptoms'])}")
            print(f"Diagnosis: {top_diagnosis['name']}")
            print(f"Confidence: {top_diagnosis['confidence']}%")
            print(f"Severity: {top_diagnosis['severity']}")
            print(f"Risk Level: {top_diagnosis['risk_level']}")
            print(f"Maintenance Time: {top_diagnosis['maintenance_time']}")
            
            # Verify
            if top_diagnosis['type'] == test['expected']:
                print("✅ PASS")
            else:
                print(f"❌ FAIL - Expected {test['expected']}, got {top_diagnosis['type']}")
        else:
            print("❌ No diagnosis found")
        
        print()
    
    print("=" * 60)
    print("Tests completed!")
    print("=" * 60)

if __name__ == '__main__':
    test_diagnosis()

