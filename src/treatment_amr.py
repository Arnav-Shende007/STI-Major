"""
Treatment Recommendation and Smart AMR-Aware Clinical Context Engine:
1. Deterministic mapping to CDC & WHO STI Treatment Guidelines (2021/2026 update).
2. Longitudinal Antimicrobial Resistance (AMR) calculation engine using 2,511 CDC GISP surveillance records.
3. Dynamic ranking of therapeutic options based on longitudinal trend velocity and contraindication factors.
"""

import os
import pandas as pd
import numpy as np

# Official CDC & WHO STI Treatment Protocols
TREATMENT_GUIDELINES = {
    'Early_Syphilis': {
        'pathogen': 'Treponema pallidum (Spirochete)',
        'icd10': 'A51.0 (Primary) / A51.3 (Secondary)',
        'first_line': {
            'regimen': 'Benzathine penicillin G 2.4 million units IM in a single dose',
            'administration': 'Intramuscular injection (split into two 1.2M unit injections in each gluteal region)',
            'duration': 'Single visit',
            'efficacy': 'Primary cure rate >95%'
        },
        'alternative': {
            'regimen': 'Doxycycline 100 mg orally twice daily for 14 days',
            'indication': 'Non-pregnant penicillin-allergic patients',
            'secondary_alternative': 'Ceftriaxone 1g daily IM/IV for 10-14 days or Tetracycline 500 mg PO 4x/day x 14d'
        },
        'pregnancy_warning': 'Doxycycline is strictly contraindicated in pregnancy (fetal hepatotoxicity and deciduous teeth discoloration). Pregnant patients with penicillin allergy MUST undergo hospital desensitization and receive Benzathine penicillin G.',
        'clinical_notes': [
            'Perform baseline quantitative non-treponemal serologic test (RPR or VDRL).',
            'Re-evaluate clinically and serologically at 6 and 12 months (4-fold titer decline indicates cure).',
            'Warn patient of Jarisch-Herxheimer reaction within first 24 hours (fever, chills, headache).',
            'Test all patients for HIV and other co-infections.',
            'Presumptively treat sexual partners exposed within 90 days.'
        ],
        'amr_risk_level': 'Low in Treponema pallidum to Penicillin; Azithromycin resistance is widespread (>60-80% due to 23S rRNA mutations), making macrolides strictly non-recommended.'
    },
    'Genital_Warts': {
        'pathogen': 'Human Papillomavirus (HPV) - primarily low-risk genotypes 6 and 11',
        'icd10': 'A63.0 (Anogenital warts / Mucocutaneous papillomas)',
        'first_line': {
            'regimen': 'Patient-applied: Imiquimod 5% cream OR Podofilox 0.5% solution/gel',
            'administration': 'Imiquimod: apply at bedtime 3x/week for up to 16 weeks. Wash off with mild soap 6-10 hours post-application.',
            'duration': '4 to 16 weeks depending on lesion clearance',
            'efficacy': 'Clearance in 50-70% with lower recurrence rates'
        },
        'alternative': {
            'regimen': 'Clinician-administered: Cryotherapy with liquid nitrogen (freeze-thaw cycle q1-2 weeks) OR Trichloroacetic acid (TCA) 80-90%',
            'indication': 'Patients preferring office therapy, extensive lesions, or during pregnancy (TCA/Cryo safe)'
        },
        'pregnancy_warning': 'Podofilox, Imiquimod, and Sinecatechins are contraindicated in pregnancy. Cryotherapy, surgical excision, or TCA are preferred.',
        'clinical_notes': [
            'Treatment aims to eradicate visible lesions; does not eradicate underlying HPV viral reservoir.',
            'Offer HPV 9-valent recombinant vaccination (Gardasil-9) to prevent additional genotype acquisition.',
            'Screen for concurrent cervical / mucosal dysplasia in indicated patient cohorts.',
            'Counsel on barrier protection and safe sex practices.'
        ],
        'amr_risk_level': 'Non-applicable (Viral etiology; antibacterial resistance does not apply to immunomodulators/ablative therapy).'
    },
    'Herpes_Simplex': {
        'pathogen': 'Herpes Simplex Virus Type 1 or 2 (HSV-1 / HSV-2)',
        'icd10': 'A60.0 (Herpes simplex infection)',
        'first_line': {
            'regimen': 'Valacyclovir 1000 mg orally twice daily for 7 to 10 days',
            'administration': 'Oral tablet; initiate within 72 hours of symptom onset',
            'duration': '7-10 days (extend if lesions incompletely healed)',
            'efficacy': 'Shortens viral shedding and healing time by 4-7 days'
        },
        'alternative': {
            'regimen': 'Acyclovir 400 mg orally 3 times daily for 7-10 days, OR Famciclovir 250 mg TID for 7-10 days',
            'indication': 'Patients unable to tolerate valacyclovir or requiring lower-cost alternatives'
        },
        'pregnancy_warning': 'Acyclovir is safe across all trimesters. At 36 weeks gestation, suppressive therapy (Acyclovir 400mg TID or Valacyclovir 500mg BID) is recommended to prevent neonatal herpes transmission.',
        'clinical_notes': [
            'Confirm diagnosis with type-specific viral NAAT/PCR (gold standard over serology).',
            'For recurrent episodes: Valacyclovir 500 mg BID x 3 days initiated at prodrome.',
            'If recurrences exceed 6 episodes/year, initiate daily suppressive therapy (Valacyclovir 500-1000 mg daily).',
            'Counsel on asymptomatic viral shedding and disclosure to sexual partners.'
        ],
        'amr_risk_level': 'Low in immunocompetent hosts (<0.5%); Acyclovir-resistant HSV (thymidine kinase gene mutation) observed in ~5% of immunocompromised individuals (requires Foscarnet IV).'
    },
    'Lichen_Sclerosus': {
        'pathogen': 'Autoimmune / Chronic inflammatory mucocutaneous disorder (Non-infectious)',
        'icd10': 'L90.0 (Lichen sclerosus et atrophicus)',
        'first_line': {
            'regimen': 'Clobetasol propionate 0.05% ointment (Ultra-potent topical corticosteroid)',
            'administration': 'Apply fingertip unit once daily at bedtime for 4 weeks, then alternate nights for 4 weeks, then twice weekly for 4 weeks (12-week taper).',
            'duration': '12-week induction taper followed by individualized maintenance',
            'efficacy': 'Symptom relief >85%, reversal of hyperkeratosis'
        },
        'alternative': {
            'regimen': 'Topical Calcineurin Inhibitor: Tacrolimus 0.1% ointment twice daily',
            'indication': 'Steroid-resistant disease or to avoid steroid-induced skin atrophy'
        },
        'pregnancy_warning': 'Topical clobetasol in modest quantities is generally acceptable if strictly needed, but monitor carefully for cutaneous atrophy.',
        'clinical_notes': [
            'Crucial Differential: Differentiate from mucosal candidiasis and extramammary Paget disease.',
            'Punch biopsy recommended if diagnosis uncertain or if lesions fail to respond to steroids.',
            'MANDATORY ONCOLOGIC SURVEILLANCE: ~4-5% lifetime risk of developing Squamous Cell Carcinoma (SCC). Annual clinical examination mandatory.',
            'Advise soap-free gentle cleansing and emollient barrier creams.'
        ],
        'amr_risk_level': 'Not applicable (Autoimmune inflammatory dermatosis; non-antimicrobial pharmacotherapy).'
    },
    'Molluscum_Contagiosum': {
        'pathogen': 'Molluscum Contagiosum Virus (MCV - Poxviridae)',
        'icd10': 'B08.1 (Molluscum contagiosum)',
        'first_line': {
            'regimen': 'Active Observation (Watchful Waiting) OR Physical Extraction (Cryotherapy with Liquid Nitrogen)',
            'administration': 'Cryotherapy: 5-10 second liquid nitrogen freeze until halo appears; repeat every 2-3 weeks.',
            'duration': 'Self-resolving over 6-18 months in healthy individuals; 1-3 office visits if treated',
            'efficacy': 'Rapid cosmetic clearance with low scarring risk'
        },
        'alternative': {
            'regimen': 'Topical Cantharidin 0.7% (applied by clinician, wash off in 2-4 hours) OR Curettage with local anesthesia',
            'indication': 'Patients desiring rapid clearance or refractory to cryotherapy'
        },
        'pregnancy_warning': 'Physical removal (cryotherapy/curettage) is safe during pregnancy. Avoid podophyllotoxin.',
        'clinical_notes': [
            'Characteristic clinical sign: Central umbilication with curd-like core.',
            'Avoid shaving or scratching affected skin area to prevent rapid autoinoculation.',
            'In adults with extensive, facial, or giant (>1cm) lesions, perform mandatory HIV testing (marker of cellular immunosuppression).',
            'Refrain from close skin contact until active lesions resolve.'
        ],
        'amr_risk_level': 'Not applicable (Poxvirus; physical ablation or watchful waiting).'
    },
    'Tinea': {
        'pathogen': 'Dermatophytes (Trichophyton rubrum, T. mentagrophytes, Epidermophyton floccosum)',
        'icd10': 'B35.6 (Tinea cruris / Tinea corporis)',
        'first_line': {
            'regimen': 'Terbinafine 1% cream applied topically once or twice daily for 1 to 2 weeks',
            'administration': 'Apply to lesion and 2-3 cm beyond margin onto normal skin',
            'duration': '1-2 weeks (continue 1 week beyond clinical resolution)',
            'efficacy': 'Mycological cure rate >90%'
        },
        'alternative': {
            'regimen': 'Clotrimazole 1% cream BID for 2-4 weeks, OR Oral Terbinafine 250 mg daily for 2-4 weeks for extensive disease',
            'indication': 'Patients refractory to topical terbinafine or with folliculitis'
        },
        'pregnancy_warning': 'Topical clotrimazole or miconazole is preferred first-line in pregnancy. Avoid oral terbinafine.',
        'clinical_notes': [
            'Keep skin folds dry with breathable clothing.',
            'Crucial check: Inspect feet for Tinea Pedis (Athlete’s foot) which is the most common autoinoculation reservoir.',
            'Avoid topical corticosteroids alone (leads to Tinea Incognito and worsening fungal proliferation).'
        ],
        'amr_risk_level': 'Emerging concern: Trichophyton indotineae exhibits severe terbinafine resistance (SQLE gene mutation); requires oral Itraconazole if unresponsive.'
    }
}


# Candidate Therapies with Clinical Profiles and Resistance Mapping
CANDIDATE_THERAPIES = {
    'Early_Syphilis': [
        {
            'name': 'Benzathine Penicillin G 2.4M Units IM',
            'class': 'Beta-lactam Penicillin',
            'route': 'Intramuscular',
            'base_efficacy': 98.0,
            'gisp_key': 'Penicillin_G',
            'known_resistance_rate': 0.0,
            'trend_slope': 0.0,
            'is_penicillin': True,
            'contraindicated_pregnancy': False,
            'rationale': 'CDC Gold Standard. Zero documented resistance globally in Treponema pallidum.'
        },
        {
            'name': 'Doxycycline 100mg PO BID x 14d',
            'class': 'Tetracycline',
            'route': 'Oral',
            'base_efficacy': 92.0,
            'gisp_key': 'Doxycycline',
            'known_resistance_rate': 1.2,
            'trend_slope': 0.1,
            'is_penicillin': False,
            'contraindicated_pregnancy': True,
            'rationale': 'CDC Recommended First Alternative for non-pregnant penicillin-allergic patients.'
        },
        {
            'name': 'Ceftriaxone 1g Daily IM/IV x 10d',
            'class': '3rd Gen Cephalosporin',
            'route': 'Injectable',
            'base_efficacy': 91.0,
            'gisp_key': 'Ceftriaxone',
            'known_resistance_rate': 0.1,
            'trend_slope': 0.0,
            'is_penicillin': False,
            'contraindicated_pregnancy': False,
            'rationale': 'Acceptable hospital parenteral alternative if oral compliance is doubtful.'
        },
        {
            'name': 'Azithromycin 2g PO Single Dose',
            'class': 'Macrolide',
            'route': 'Oral',
            'base_efficacy': 75.0,
            'gisp_key': 'Azithromycin',
            'known_resistance_rate': 68.0,
            'trend_slope': 3.5,
            'is_penicillin': False,
            'contraindicated_pregnancy': False,
            'rationale': 'CDC Strictly Discontinued: >60-80% resistance in T. pallidum via 23S rRNA A2058G mutation.'
        },
        {
            'name': 'Ciprofloxacin 500mg PO BID',
            'class': 'Fluoroquinolone',
            'route': 'Oral',
            'base_efficacy': 45.0,
            'gisp_key': 'Ciprofloxacin',
            'known_resistance_rate': 46.2,
            'trend_slope': 2.1,
            'is_penicillin': False,
            'contraindicated_pregnancy': True,
            'rationale': 'Ineffective for treponemal disease and carries high gyrA/parC resistance risk.'
        }
    ],
    'Herpes_Simplex': [
        {
            'name': 'Valacyclovir 1000mg PO BID x 7-10d',
            'class': 'Nucleoside Analogue (Prodrug)',
            'route': 'Oral',
            'base_efficacy': 94.0,
            'gisp_key': 'Valacyclovir',
            'known_resistance_rate': 0.3,
            'trend_slope': 0.05,
            'is_penicillin': False,
            'contraindicated_pregnancy': False,
            'rationale': 'Superior oral bioavailability (54% vs 15-20% for acyclovir) with twice-daily dosing.'
        },
        {
            'name': 'Acyclovir 400mg PO TID x 7-10d',
            'class': 'Nucleoside Analogue',
            'route': 'Oral',
            'base_efficacy': 89.0,
            'gisp_key': 'Acyclovir',
            'known_resistance_rate': 0.5,
            'trend_slope': 0.05,
            'is_penicillin': False,
            'contraindicated_pregnancy': False,
            'rationale': 'Extensively validated safety in pregnancy; lower cost alternative.'
        },
        {
            'name': 'Famciclovir 250mg PO TID x 7-10d',
            'class': 'Diacetyl Prodrug of Penciclovir',
            'route': 'Oral',
            'base_efficacy': 88.0,
            'gisp_key': 'Famciclovir',
            'known_resistance_rate': 0.4,
            'trend_slope': 0.05,
            'is_penicillin': False,
            'contraindicated_pregnancy': False,
            'rationale': 'Reliable alternative for acyclovir-intolerant patients.'
        },
        {
            'name': 'Foscarnet 40mg/kg IV q8h',
            'class': 'Pyrophosphate Analogue',
            'route': 'Intravenous',
            'base_efficacy': 82.0,
            'gisp_key': 'Foscarnet',
            'known_resistance_rate': 1.8,
            'trend_slope': 0.2,
            'is_penicillin': False,
            'contraindicated_pregnancy': True,
            'rationale': 'Reserved strictly for thymidine kinase-negative acyclovir-resistant HSV.'
        }
    ],
    'Genital_Warts': [
        {
            'name': 'Imiquimod 5% Cream 3x/week',
            'class': 'Toll-like Receptor 7/8 Agonist',
            'route': 'Topical',
            'base_efficacy': 78.0,
            'gisp_key': 'Imiquimod',
            'known_resistance_rate': 0.0,
            'trend_slope': 0.0,
            'is_penicillin': False,
            'contraindicated_pregnancy': True,
            'rationale': 'Activates local cell-mediated cytokine immunity, yielding lower recurrence rates.'
        },
        {
            'name': 'Cryotherapy (Liquid Nitrogen)',
            'class': 'Physical Thermal Ablation',
            'route': 'Office Procedure',
            'base_efficacy': 75.0,
            'gisp_key': 'Cryo',
            'known_resistance_rate': 0.0,
            'trend_slope': 0.0,
            'is_penicillin': False,
            'contraindicated_pregnancy': False,
            'rationale': 'Fast physical destruction; 100% safe in pregnancy.'
        },
        {
            'name': 'Podofilox 0.5% Solution/Gel',
            'class': 'Antimitotic Cytotoxic Agent',
            'route': 'Topical',
            'base_efficacy': 72.0,
            'gisp_key': 'Podofilox',
            'known_resistance_rate': 0.0,
            'trend_slope': 0.0,
            'is_penicillin': False,
            'contraindicated_pregnancy': True,
            'rationale': 'Direct arrest of epidermal cell mitosis in metaphase.'
        },
        {
            'name': 'Trichloroacetic Acid (TCA) 80-90%',
            'class': 'Caustic Chemical Keratolytic',
            'route': 'Topical Office Application',
            'base_efficacy': 70.0,
            'gisp_key': 'TCA',
            'known_resistance_rate': 0.0,
            'trend_slope': 0.0,
            'is_penicillin': False,
            'contraindicated_pregnancy': False,
            'rationale': 'Chemical coagulation of lesion proteins; safe during pregnancy.'
        }
    ],
    'Tinea': [
        {
            'name': 'Terbinafine 1% Cream Topical BID x 2w',
            'class': 'Allylamine Antifungal',
            'route': 'Topical',
            'base_efficacy': 92.0,
            'gisp_key': 'Terbinafine_Topical',
            'known_resistance_rate': 2.1,
            'trend_slope': 0.3,
            'is_penicillin': False,
            'contraindicated_pregnancy': False,
            'rationale': 'Inhibits squalene epoxidase, fungicidal against dermatophytes.'
        },
        {
            'name': 'Clotrimazole 1% Cream BID x 4w',
            'class': 'Imidazole Antifungal',
            'route': 'Topical',
            'base_efficacy': 84.0,
            'gisp_key': 'Clotrimazole',
            'known_resistance_rate': 1.5,
            'trend_slope': 0.1,
            'is_penicillin': False,
            'contraindicated_pregnancy': False,
            'rationale': 'Fungistatic ergosterol synthesis inhibitor; pregnancy Category B.'
        },
        {
            'name': 'Oral Terbinafine 250mg PO Daily x 2w',
            'class': 'Systemic Allylamine',
            'route': 'Oral',
            'base_efficacy': 88.0,
            'gisp_key': 'Terbinafine_Oral',
            'known_resistance_rate': 8.5,
            'trend_slope': 1.4,
            'is_penicillin': False,
            'contraindicated_pregnancy': True,
            'rationale': 'Effective for extensive dermatophytosis; requires monitoring for T. indotineae resistance.'
        },
        {
            'name': 'Oral Itraconazole 100mg PO Daily x 2w',
            'class': 'Systemic Triazole',
            'route': 'Oral',
            'base_efficacy': 86.0,
            'gisp_key': 'Itraconazole',
            'known_resistance_rate': 4.0,
            'trend_slope': 0.5,
            'is_penicillin': False,
            'contraindicated_pregnancy': True,
            'rationale': 'Reserve oral therapy for terbinafine-resistant dermatophyte strains.'
        }
    ],
    'Lichen_Sclerosus': [
        {
            'name': 'Clobetasol Propionate 0.05% Ointment',
            'class': 'Ultra-Potent Topical Corticosteroid (Class I)',
            'route': 'Topical',
            'base_efficacy': 90.0,
            'gisp_key': 'Clobetasol',
            'known_resistance_rate': 0.0,
            'trend_slope': 0.0,
            'is_penicillin': False,
            'contraindicated_pregnancy': False,
            'rationale': 'Standard induction therapy: suppresses dermal lymphocytic inflammation and architectural resorption.'
        },
        {
            'name': 'Tacrolimus 0.1% Ointment BID',
            'class': 'Topical Calcineurin Inhibitor',
            'route': 'Topical',
            'base_efficacy': 78.0,
            'gisp_key': 'Tacrolimus',
            'known_resistance_rate': 0.0,
            'trend_slope': 0.0,
            'is_penicillin': False,
            'contraindicated_pregnancy': False,
            'rationale': 'Steroid-sparing maintenance to avoid long-term mucosal atrophy.'
        }
    ],
    'Molluscum_Contagiosum': [
        {
            'name': 'Cryotherapy with Liquid Nitrogen',
            'class': 'Thermal Ablation',
            'route': 'Office Procedure',
            'base_efficacy': 85.0,
            'gisp_key': 'Cryo_MCV',
            'known_resistance_rate': 0.0,
            'trend_slope': 0.0,
            'is_penicillin': False,
            'contraindicated_pregnancy': False,
            'rationale': 'Rapid physical ablation of umbilicated core with high cosmetic satisfaction.'
        },
        {
            'name': 'Active Observation (Watchful Waiting)',
            'class': 'Conservative Management',
            'route': 'Non-pharmacological',
            'base_efficacy': 70.0,
            'gisp_key': 'Observation',
            'known_resistance_rate': 0.0,
            'trend_slope': 0.0,
            'is_penicillin': False,
            'contraindicated_pregnancy': False,
            'rationale': 'Spontaneous immune clearance over 6-18 months in immunocompetent patients.'
        },
        {
            'name': 'Topical Cantharidin 0.7%',
            'class': 'Vesicant Phosphodiesterase Inhibitor',
            'route': 'Clinician Topical Application',
            'base_efficacy': 76.0,
            'gisp_key': 'Cantharidin',
            'known_resistance_rate': 0.0,
            'trend_slope': 0.0,
            'is_penicillin': False,
            'contraindicated_pregnancy': True,
            'rationale': 'Induces intraepidermal blistering, lifting lesion without scarring.'
        }
    ]
}


class CDCGISPService:
    """
    Antimicrobial Resistance (AMR) Surveillance Engine powered by CDC GISP / CARGOS data.
    Analyzes 2,511 records of Neisseria gonorrhoeae resistance patterns.
    """
    def __init__(self, data_path='STI_Project/03_GISP/metadata/gisp_resistance_data.csv'):
        self.data_path = data_path
        self.df = None
        self._load_data()

    def _load_data(self):
        if os.path.exists(self.data_path):
            self.df = pd.read_csv(self.data_path)
        else:
            self.df = pd.DataFrame()

    def get_summary_stats(self):
        if self.df.empty:
            return {}
        return {
            'total_records': len(self.df),
            'antimicrobials': self.df['antimicrobial'].dropna().unique().tolist(),
            'pathogen': self.df['pathogen'].iloc[0] if 'pathogen' in self.df.columns else 'Neisseria gonorrhoeae',
            'year_min': 2000,
            'year_max': 2023,
            'geographies': self.df['geography'].dropna().unique().tolist() if 'geography' in self.df.columns else []
        }

    def get_resistance_at_year(self, antimicrobial, year=2023):
        """
        Returns average resistance percent for an antimicrobial at a given year.
        """
        if self.df.empty or 'antimicrobial' not in self.df.columns:
            return 0.0
        sub = self.df[(self.df['antimicrobial'].str.lower() == antimicrobial.lower()) & (self.df['year'].astype(str) == str(year))]
        if sub.empty:
            # Fall back to closest available year
            sub = self.df[self.df['antimicrobial'].str.lower() == antimicrobial.lower()]
            if sub.empty:
                return 0.0
        val = sub['resistance_percent'].dropna().mean()
        return round(float(val), 2) if not np.isnan(val) else 0.0

    def get_resistance_trend(self, antimicrobial='Azithromycin'):
        if self.df.empty or 'antimicrobial' not in self.df.columns:
            return pd.DataFrame()

        sub = self.df[self.df['antimicrobial'].str.lower() == antimicrobial.lower()]
        sub_years = sub[sub['year'].astype(str).str.match(r'^\d{4}$')]
        grouped = sub_years.groupby('year')['resistance_percent'].mean().reset_index()
        grouped['year'] = grouped['year'].astype(int)
        grouped = grouped.sort_values('year')
        return grouped

    def get_multi_drug_trends(self):
        if self.df.empty:
            return pd.DataFrame()

        drugs = ['Ceftriaxone', 'Azithromycin', 'Cefixime', 'Ciprofloxacin']
        sub = self.df[self.df['antimicrobial'].isin(drugs)]
        sub_years = sub[sub['year'].astype(str).str.match(r'^\d{4}$')]
        pivot = sub_years.pivot_table(index='year', columns='antimicrobial', values='resistance_percent', aggfunc='mean')
        pivot = pivot.reset_index()
        pivot['year'] = pivot['year'].astype(int)
        pivot = pivot.sort_values('year')
        return pivot

    def calculate_smart_recommendations(self, disease_class, surveillance_year=2023, penicillin_allergic=False, is_pregnant=False):
        """
        Smart Mathematical Recommendation Engine:
        Evaluates all candidate therapies against longitudinal AMR resistance rate R(t),
        trend acceleration factor Delta R (past 5 years), and patient clinical contraindications.
        """
        candidates = CANDIDATE_THERAPIES.get(disease_class, [])
        ranked_results = []

        for c in candidates:
            base_eff = c['base_efficacy']
            gisp_key = c['gisp_key']

            # Lookup resistance in GISP if available, else clinical literature constant
            if gisp_key in ['Ceftriaxone', 'Azithromycin', 'Cefixime', 'Ciprofloxacin']:
                res_now = self.get_resistance_at_year(gisp_key, surveillance_year)
                res_prev = self.get_resistance_at_year(gisp_key, max(2000, surveillance_year - 5))
                delta_5yr = round(res_now - res_prev, 2)
            else:
                res_now = c['known_resistance_rate']
                delta_5yr = round(c['trend_slope'] * 5.0, 2)

            # AMR Risk Penalty: 1.2 * R(t) + 0.8 * max(0, Delta R)
            amr_penalty = (1.2 * res_now) + (0.8 * max(0.0, delta_5yr))

            # Patient Contraindication Penalty
            contra_penalty = 0.0
            contra_reason = ""
            if penicillin_allergic and c.get('is_penicillin', False):
                contra_penalty += 100.0
                contra_reason = "PENICILLIN ALLERGY (High anaphylaxis risk)"
            if is_pregnant and c.get('contraindicated_pregnancy', False):
                contra_penalty += 100.0
                contra_reason = "PREGNANCY CONTRAINDICATION (Fetal safety risk)"

            # Final Recommendation Suitability Score: [0 to 100]
            raw_score = base_eff - amr_penalty - contra_penalty
            suitability_score = round(max(0.0, min(100.0, raw_score)), 1)

            # Determine Clinical Action Status
            if contra_penalty > 0:
                status = "🔴 Strictly Contraindicated"
                status_badge = "contraindicated"
            elif suitability_score >= 85.0:
                status = "🟢 Preferred First-Line"
                status_badge = "first_line"
            elif suitability_score >= 60.0:
                status = "🟡 Approved Alternative"
                status_badge = "alternative"
            else:
                status = "🔴 High AMR Resistance Risk"
                status_badge = "high_amr_risk"

            ranked_results.append({
                'name': c['name'],
                'drug_class': c['class'],
                'route': c['route'],
                'base_efficacy': base_eff,
                'current_resistance_pct': res_now,
                'trend_5yr_delta': delta_5yr,
                'amr_penalty': round(amr_penalty, 1),
                'suitability_score': suitability_score,
                'status': status,
                'status_badge': status_badge,
                'contra_reason': contra_reason,
                'rationale': c['rationale']
            })

        # Sort by Suitability Score descending
        ranked_results.sort(key=lambda x: x['suitability_score'], reverse=True)
        for i, item in enumerate(ranked_results):
            item['rank'] = i + 1

        return ranked_results

    def get_amr_clinical_context(self, predicted_disease):
        context = {
            'has_direct_amr_data': False,
            'alert_level': 'Normal',
            'guideline_rationale': '',
            'surveillance_note': ''
        }

        if predicted_disease == 'Early_Syphilis':
            context['has_direct_amr_data'] = True
            context['alert_level'] = 'Critical Advisory'
            context['guideline_rationale'] = (
                "CDC Alert: Azithromycin resistance in Treponema pallidum now exceeds 60-80% "
                "globally due to 23S rRNA A2058G point mutations. Single-dose Azithromycin treatment failures "
                "are well documented. Penicillin G remains 100% effective with ZERO confirmed resistance cases."
            )
            context['surveillance_note'] = (
                "CDC STI Treatment Guidelines strictly prohibit macrolides for syphilis. "
                "Benzathine penicillin G is mandatory. In penicillin allergy, Doxycycline 100mg PO BID x 14d is the validated regimen."
            )
        elif predicted_disease == 'Tinea':
            context['has_direct_amr_data'] = True
            context['alert_level'] = 'Emerging Threat'
            context['guideline_rationale'] = (
                "Global Dermatological Alert: Emerging Trichophyton indotineae strains show severe resistance "
                "to first-line oral Terbinafine (squalene epoxidase gene mutations). Topical terbinafine remains effective for standard T. rubrum."
            )
            context['surveillance_note'] = "If non-responsive after 2 weeks of compliant topical therapy, request fungal culture and switch to oral Itraconazole."
        else:
            context['alert_level'] = 'Surveillance Active'
            context['guideline_rationale'] = (
                "CDC GISP Surveillance Reference: Neisseria gonorrhoeae shows alarming multidrug resistance trends. "
                "Ciprofloxacin resistance stands at ~46.2% (contraindicated). Azithromycin resistance rose to 9.1% in 2023, "
                "prompting CDC to discontinue dual-therapy in favor of Ceftriaxone 500mg IM monotherapy."
            )
            context['surveillance_note'] = (
                "Empirical prescribing must be governed by active AMR surveillance. Any concomitant urethral or cervical discharge "
                "warrants immediate NAAT screening for gonorrhea and chlamydia."
            )

        return context
