"""
Inference Engine untuk Sistem Pakar Identifikasi Kerusakan Mesin Industri
Menggunakan Forward Chaining dengan Certainty Factor (MYCIN)
"""

import json
from typing import Dict, List, Tuple


class InferenceEngine:
    def __init__(self, knowledge_base_path: str, diagnosis_data_path: str):
        """Initialize inference engine dengan knowledge base"""
        with open(knowledge_base_path, 'r', encoding='utf-8') as f:
            self.kb = json.load(f)
        
        with open(diagnosis_data_path, 'r', encoding='utf-8') as f:
            self.diagnosis_data = json.load(f)
        
        self.rules = self.kb['rules']
        self.symptoms = self.kb['symptoms']
        
    def combine_cf(self, cf1: float, cf2: float) -> float:
        """
        Kombinasi Certainty Factor menggunakan formula MYCIN
        Untuk dua evidence yang mendukung hypothesis yang sama
        """
        if cf1 >= 0 and cf2 >= 0:
            return cf1 + cf2 * (1 - cf1)
        elif cf1 <= 0 and cf2 <= 0:
            return cf1 + cf2 * (1 + cf1)
        else:
            return (cf1 + cf2) / (1 - min(abs(cf1), abs(cf2)))
    
    def calculate_rule_cf(self, rule: Dict, evidence: List[str], partial_match: bool = True) -> float:
        """
        Hitung CF untuk satu rule berdasarkan evidence yang ada
        Dengan opsi partial matching
        """
        # Cek apakah semua gejala dalam rule ada di knowledge base
        if not all(cond in self.symptoms for cond in rule['if']):
            return 0.0
        
        # Check apakah semua kondisi dalam rule terpenuhi
        rule_symptoms = set(rule['if'])
        evidence_set = set(evidence)
        
        if not rule_symptoms.issubset(evidence_set):
            # Partial matching: jika sebagian besar gejala cocok
            if partial_match:
                overlap = rule_symptoms.intersection(evidence_set)
                if len(overlap) > 0 and len(rule_symptoms) <= 2:
                    # Untuk rules sederhana, partial match OK
                    match_ratio = len(overlap) / len(rule_symptoms)
                    if match_ratio >= 0.5:  # Minimal 50% match
                        # Reduce CF karena tidak semua gejala ada
                        evidence_cfs = [self.symptoms[cond]['cf'] for cond in overlap if cond in self.symptoms]
                        if not evidence_cfs:
                            return 0.0
                        min_cf = min(evidence_cfs)
                        rule_cf = rule['cf']
                        # Kurangi CF berdasarkan match ratio
                        return (min_cf * rule_cf) * match_ratio
            return 0.0
        
        # CF rule = CF evidence * CF rule
        # Ambil CF minimum dari semua evidence (untuk AND)
        evidence_cfs = [self.symptoms[cond]['cf'] for cond in rule['if']]
        if not evidence_cfs:
            return 0.0
        
        min_cf = min(evidence_cfs)
        rule_cf = rule['cf']
        
        # CF(rule) = CF(evidence) * CF(rule definition)
        return min_cf * rule_cf
    
    def forward_chaining(self, selected_symptoms: List[str]) -> List[Dict]:
        """
        Proses inference dengan Forward Chaining
        """
        # Working Memory: symptoms yang dipilih user
        working_memory = set(selected_symptoms)
        results = {}
        reasoning_process = []
        
        # Loop untuk tiap rule
        for rule in self.rules:
            rule_cf = self.calculate_rule_cf(rule, selected_symptoms)
            
            if rule_cf > 0:
                conclusion = rule['then']
                
                evidence_names = []
                for s in rule['if']:
                    if s in selected_symptoms and s in self.symptoms:
                        evidence_names.append(self.symptoms[s]['name'])
                
                reasoning_process.append({
                    'rule_id': rule['id'],
                    'rule_description': rule['description'],
                    'evidence': evidence_names,
                    'conclusion': conclusion,
                    'cf': rule_cf
                })
                
                # Kombinasi CF jika ada multiple rules untuk conclusion yang sama
                if conclusion in results:
                    results[conclusion] = self.combine_cf(results[conclusion], rule_cf)
                else:
                    results[conclusion] = rule_cf
        
        # Format hasil diagnosis
        diagnoses = []
        for diagnosis_key, cf in sorted(results.items(), key=lambda x: x[1], reverse=True):
            diagnosis_info = {
                'type': diagnosis_key,
                'name': self.diagnosis_data[diagnosis_key]['name'],
                'description': self.diagnosis_data[diagnosis_key]['description'],
                'confidence': round(cf * 100, 2),
                'cf_value': round(cf, 4),
                'causes': self.diagnosis_data[diagnosis_key]['causes'],
                'solutions': self.diagnosis_data[diagnosis_key]['solutions'],
                'severity': self.diagnosis_data[diagnosis_key]['severity'],
                'maintenance_time': self.diagnosis_data[diagnosis_key]['maintenance_time'],
                'risk_level': self.diagnosis_data[diagnosis_key]['risk_level'],
                'tools_required': self.diagnosis_data[diagnosis_key]['tools_required']
            }
            diagnoses.append(diagnosis_info)
        
        return diagnoses, reasoning_process
    
    def get_symptoms_list(self) -> List[Dict]:
        """Ambil daftar semua gejala"""
        symptoms_list = []
        for key, value in self.symptoms.items():
            symptoms_list.append({
                'id': key,
                'name': value['name'],
                'cf': value['cf']
            })
        return sorted(symptoms_list, key=lambda x: x['id'])


if __name__ == '__main__':
    # Test inference engine
    engine = InferenceEngine('knowledge_base.json', 'diagnosis_data.json')
    
    # Test case
    test_symptoms = ['Q2', 'Q8']
    diagnoses, reasoning = engine.forward_chaining(test_symptoms)
    
    print("Diagnoses:")
    for d in diagnoses:
        print(f"- {d['name']}: {d['confidence']}% confidence")
    
    print("\nReasoning:")
    for r in reasoning:
        print(f"- {r['rule_id']}: {r['conclusion']} (CF={r['cf']:.4f})")

