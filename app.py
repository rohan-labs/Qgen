import streamlit as st
import anthropic
from typing import List, Dict

# Page configuration
st.set_page_config(
    page_title="Claude Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key" not in st.session_state:
    # Try to get API key from secrets.toml
    st.session_state.api_key = st.secrets.get("ANTHROPIC_API_KEY", "") if "ANTHROPIC_API_KEY" in st.secrets else ""
    
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = """SBA Purpose
You are a production model designed to produce difficult mock exam questions for medical students.
You must produce the following question sets:
Question Set
Defined as
Question Stem
Lead-In question
Answer options
Correct answer
Why the question set is difficult
Explanations
Module categorisation
Presentation categorisation
Your tone must be in the most medically complex and succinct tone and you must use long and precise medical terminology. Include red-herrings to make the question complex.
Question Stem
It must be challenging for the student and be made in these steps: 

Step 1 - Write the patient's age and gender at the start for example "A 42-year-old male" or "A 5-year-old girl exhibits".
Step 2 - Write the patient's presenting complaint. Use your information regarding the features, signs and symptoms of the condition to do this. You must use various adjectives and synonyms to describe the signs and symptoms and investigation findings in unique ways. When making multiple question stems, do not repeat question stems for different questions on the same condition. Get creative!!

Step 3 - Never give away the diagnosis in the question stem. All questions MUST BE MULTI-STEPPED by explaining the features of the condition without explicitly mentioning the condition name.

Step 4 - Include red herrings about common differentials/answer options. Use the differentials provided or from your knowledge to include their features within the question stem. Provide them with subtle or less obvious details that allow for multiple possible answers.

Step 5 - Write the investigations and examination findings. Investigation findings must be described and not give away the diagnosis, For example, "Transvaginal ultrasound finding = 6mm gestational sac implanted in the left fallopian tube" NOT "Transvaginal ultrasound confirms an ectopic pregnancy". Giving raw data over formulation is best for example, "her temperature is 38.5°C and pulse rate is 121 bpm" requires more clinical knowledge and experience than "she is pyrexic and tachycardic."

Step 6 - Write down the patient's risk factors and medical history. Use risk factors and medical history from the information provided to you to test the user as to what the most likely diagnosis is. This can allow for your question stems to be even more vague and challenging, as the user has to use probability to assume a diagnosis.

Lead-In question
Step 1 - The lead-in question should only be answerable alongside the stem. For example, "Given the most likely diagnosis, what is the most likely adverse effect of the most appropriate management option?" requires reading the stem to answer, while "What is the most common adverse effect of ramipril?" is a freestanding question and must be avoided. The lead-in must express uncertainty, asking for the "most likely" diagnosis or the "most appropriate" investigation, implying all options are plausible but one is "most correct." Ensure lead-in questions are positive, as negative questions provide little value.
Answer options
Step 1 - Provide five multiple-choice answers (A through to E) for each question. Ensure every answer belongs to the same domain/address of the same topic. The answer options should all be from the same topic or domain. Retrieve this information from the information provided. This makes discrimination more challenging for the candidate. Step 2 - You must avoid and NOT include other options e.g. "A and C" or "all of the above" as options.Step 3 - Include answer pairs e.g. "A - 250mg TDS Amoxicillin and IV Fluids" "B - 500mg TDS Amoxicillin and IV fluids"
Correct Answer
Ensure the correct answer is not always e.g. Option A. Change it up when positioning the right answer.
Why the question is difficult
You must explain why the question you produced was difficult and multi-stepped commenting on the following:
the specific mult-stepped thinking a student would need to think about the question
why the answer options are good as they are of the same domain and have only a small difference compared with the right answer (e.g. 500mg Amoxicillin = correct answer, 450mg Amoxicillin = incorrect answer, 500mg Flucloxcillin = incorrect answer).
Explanations
For each answer option, please explain why the answer is wrong or right in this context You use the document provided to support your explanations.
Module and Presentation Selection
You must categorise with the following lists from the UKMLA"""

# Page header
st.title("Claude Chatbot")
st.markdown("Chat with Claude using the Anthropic API")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # API key input
    api_key = st.text_input(
        "Anthropic API Key", 
        value=st.session_state.api_key,
        type="password",
        help="Enter your Anthropic API key. It will be securely stored in the session state."
    )
    if api_key:
        st.session_state.api_key = api_key
    
    # System message input
    st.subheader("System Instructions")
    system_prompt = st.text_area(
        "Edit Claude's Instructions",
        value=st.session_state.system_prompt,
        height=300
    )
    if system_prompt != st.session_state.system_prompt:
        st.session_state.system_prompt = system_prompt
        # Reset messages if instructions change
        if st.button("Apply Changes"):
            st.session_state.messages = []
            st.rerun()
    
    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
        
    # Reference Lists in sidebar
    st.header("Reference Lists")
    
    with st.expander("Module List", expanded=False):
        module_list = """Module
1 - Acute and emergency,
2 - Cancer,
3 - Cardiovascular,
4 - Child health,
5 - Clinical Haematology,
6 - Clinical imaging,
7 - Dermatology,
8 - Ear, nose and throat,
9 - Endocrine and metabolic,
10 - Gastrointestinal including liver,
11 - General practice and primary healthcare,
12 - Infection,
13 - Mental health,
14 - Musculoskeletal,
15 - Neurosciences,
16 - Obstetrics and gynaecology,
17 - Ophthalmology,
18 - Perioperative medicine and anaesthesia,
19 - Renal and urology,
20 - Respiratory,
21 - Surgery,
22 - Allergy and immunology,
23 - Clinical biochemistry,
24 - Clinical pharmacology and therapeutics,
25 - Genetics and genomics,
26 - Laboratory haematology,
27 - Palliative and end of life care,
28 - Social and population health,
57 - Geriatric"""
        st.code(module_list, language=None)
    
    with st.expander("Presentation List", expanded=False):
        presentation_list = """Presentations
1. Abdominal distension,
2. Abdominal mass,
3. Abnormal cervical smear result,
4. Abnormal development/developmental delay,
5. Abnormal eating or exercising behavior,
6. Abnormal involuntary movements,
7. Abnormal urinalysis,
8. Acute abdominal pain,
9. Acute and chronic pain management,
10. Acute change in or loss of vision,
11. Acute joint pain/swelling,
12. Acute kidney injury,
13. Acute rash,
14. Addiction,
15. Allergies,
16. Altered sensation, numbness and tingling,
17. Amenorrhoea,
18. Anaphylaxis,
19. Anosmia,
20. Anxiety, phobias, OCD,
21. Ascites,
22. Auditory hallucinations,
23. Back pain,
24. Behaviour/personality change,
25. Behavioural difficulties in childhood,
26. Bites and stings,
27. Blackouts and faints,
28. Bleeding antepartum,
29. Bleeding from lower GI tract,
30. Bleeding from upper GI tract,
31. Bleeding postpartum,
32. Bone pain,
33. Breast lump,
34. Breast tenderness/pain,
35. Breathlessness,
36. Bruising,
37. Burns,
38. Cardiorespiratory arrest,
39. Change in bowel habit,
40. Change in stool color,
41. Chest pain,
42. Child abuse,
43. Chronic abdominal pain,
44. Chronic joint pain/stiffness,
45. Chronic kidney disease,
46. Chronic rash,
47. Cold, painful, pale, pulseless leg/foot,
48. Complications of labour,
49. Confusion,
50. Congenital abnormalities,
51. Constipation,
52. Contraception request/advice,
53. Cough,
54. Crying baby,
55. Cyanosis,
56. Death and dying,
57. Decreased appetite,
58. Decreased/loss of consciousness,
59. Dehydration,
60. Deteriorating patient,
61. Diarrhoea,
62. Difficulty with breastfeeding,
63. Diplopia,
64. Dizziness,
65. Driving advice,
66. Dysmorphic child,
67. Ear and nasal discharge,
68. Elation/elated mood,
69. Elder abuse,
70. Electrolyte abnormalities,
71. End of life care/symptoms of terminal illness,
72. Epistaxis,
73. Erectile dysfunction,
74. Eye pain/discomfort,
75. Eye trauma,
76. Facial pain,
77. Facial weakness,
78. Facial/periorbital swelling,
79. Faecal incontinence,
80. Falls,
81. Family history of possible genetic disorder,
82. Fasciculation,
83. Fatigue,
84. Fever,
85. Fit notes,
86. Fits/seizures,
87. Fixed abnormal beliefs,
88. Flashes and floaters in visual fields,
89. Food intolerance,
90. Foreign body in eye,
91. Frailty,
92. Gradual change in or loss of vision,
93. Gynaecomastia,
94. Haematuria,
95. Haemoptysis,
96. Head injury,
97. Headache,
98. Hearing loss,
99. Heart murmurs,
100. Hoarseness and voice change,
101. Hyperemesis,
102. Hypertension,
103. Immobility,
104. Incidental findings,
105. Infant feeding problems,
106. Intrauterine death,
107. Jaundice,
108. Labour,
109. Lacerations,
110. Learning disability,
111. Limb claudication,
112. Limb weakness,
113. Limp,
114. Loin pain,
115. Loss of libido,
116. Loss of red reflex,
117. Low blood pressure,
118. Low mood/affective problems,
119. Lump in groin,
120. Lymphadenopathy,
121. Massive haemorrhage,
122. Melaena,
123. Memory loss,
124. Menopausal problems,
125. Menstrual problems,
126. Mental capacity concerns,
127. Mental health problems in pregnancy or postpartum,
128. Misplaced nasogastric tube,
129. Muscle pain/myalgia,
130. Musculoskeletal deformities,
131. Nail abnormalities,
132. Nasal obstruction,
133. Nausea,
134. Neck lump,
135. Neck pain/stiffness,
136. Neonatal death or cot death,
137. Neuromuscular weakness,
138. Night sweats,
139. Nipple discharge,
140. Normal pregnancy and antenatal care,
141. Oliguria,
142. Organomegaly,
143. Overdose,
144. Pain on inspiration,
145. Painful ear,
146. Painful sexual intercourse,
147. Painful swollen leg,
148. Pallor,
149. Palpitations,
150. Pelvic mass,
151. Pelvic pain,
152. Perianal symptoms,
153. Peripheral oedema and ankle swelling,
154. Petechial rash,
155. Pleural effusion,
156. Poisoning,
157. Polydipsia (thirst),
158. Post-surgical care and complications,
159. Pregnancy risk assessment,
160. Prematurity,
161. Pressure of speech,
162. Pruritus,
163. Ptosis,
164. Pubertal development,
165. Purpura,
166. Rectal prolapse,
167. Red eye,
168. Reduced/change in fetal movements,
169. Scarring,
170. Scrotal/testicular pain and/or lump/swelling,
171. Self-harm,
172. Shock,
173. Skin lesion,
174. Skin or subcutaneous lump,
175. Skin ulcers,
176. Sleep problems,
177. Small for gestational age/large for gestational age,
178. Snoring,
179. Soft tissue injury,
180. Somatisation/medically unexplained physical symptoms,
181. Sore throat,
182. Speech and language problems,
183. Squint,
184. Stridor,
185. Struggling to cope at home,
186. Subfertility,
187. Substance misuse,
188. Suicidal thoughts,
189. Swallowing problems,
190. The sick child,
191. Threats to harm others,
192. Tinnitus,
193. Trauma,
194. Travel health advice,
195. Tremor,
196. Unsteadiness,
197. Unwanted pregnancy and termination,
198. Urethral discharge and genital ulcers/warts,
199. Urinary incontinence,
200. Urinary symptoms,
201. Vaccination,
202. Vaginal discharge,
203. Vaginal prolapse,
204. Vertigo,
205. Visual hallucinations,
206. Vomiting,
207. Vulval itching/lesion,
208. Vulval/vaginal lump,
209. Weight gain,
210. Weight loss,
211. Wellbeing checks,
212. Wheeze"""
        st.code(presentation_list, language=None)
    
    with st.expander("Condition List", expanded=False):
        condition_list = """Condition name
1. Acid-base abnormality
2. Acne vulgaris
3. Acoustic neuroma
4. Acute bronchitis
5. Acute cholangitis
6. Acute coronary syndromes
7. Acute glaucoma
8. Acute kidney injury
9. Acute pancreatitis
10. Acute stress reaction
11. Addison's disease
12. Adverse drug effects
13. Alcoholic hepatitis
14. Allergic disorder
15. Anaemia
16. Anal fissure
17. Anaphylaxis
18. Aneurysms, ischaemic limb and occlusions
19. Ankylosing spondylitis
20. Anxiety disorder: generalised
21. Anxiety disorder: post-traumatic stress disorder
22. Anxiety, phobias, OCD
23. Aortic aneurysm
24. Aortic dissection
25. Aortic valve disease
26. Appendicitis
27. Arrhythmias
28. Arterial thrombosis
29. Arterial ulcers
30. Asbestos-related lung disease
31. Ascites
32. Asthma
33. Asthma COPD overlap syndrome
34. Atopic dermatitis and eczema
35. Atrophic vaginitis
36. Attention deficit hyperactivity disorder
37. Autism spectrum disorder
38. Bacterial vaginosis
39. Basal cell carcinoma
40. Bell's palsy
41. Benign eyelid disorders
42. Benign paroxysmal positional vertigo
43. Benign prostatic hyperplasia
44. Biliary atresia
45. Bipolar affective disorder
46. Bladder cancer
47. Blepharitis
48. Brain abscess
49. Brain metastases
50. Breast abscess/mastitis
51. Breast cancer
52. Breast cysts
53. Bronchiectasis
54. Bronchiolitis
55. Bursitis
56. Candidiasis
57. Cardiac arrest
58. Cardiac failure
59. Cataracts
60. Cellulitis
61. Central retinal arterial occlusion
62. Cerebral palsy and hypoxic-ischaemic encephalopathy
63. Cervical cancer
64. Cervical screening (HPV)
65. Chlamydia
66. Cholecystitis
67. Chronic fatigue syndrome
68. Chronic glaucoma
69. Chronic kidney disease
70. Chronic obstructive pulmonary disease
71. Cirrhosis
72. Coeliac disease
73. Colorectal tumours
74. Compartment syndrome
75. Conjunctivitis
76. Constipation
77. Contact dermatitis
78. Cord prolapse
79. Covid-19
80. Croup
81. Crystal arthropathy
82. Cushing's syndrome
83. Cutaneous fungal infection
84. Cutaneous warts
85. Cystic fibrosis
86. Deep vein thrombosis
87. Dehydration
88. Delirium
89. Dementias
90. Depression
91. Developmental delay
92. Diabetes in pregnancy (gestational and pre-existing)
93. Diabetes insipidus
94. Diabetes mellitus type 1 and type 2
95. Diabetic eye disease
96. Diabetic ketoacidosis
97. Diabetic nephropathy
98. Diabetic neuropathy
99. Disease prevention/screening
100. Disseminated intravascular coagulation
101. Diverticular disease
102. Down's syndrome
103. Drug overdose
104. Eating disorders
105. Ectopic pregnancy
106. Encephalitis
107. Endometrial cancer
108. Endometriosis
109. Epididymitis and orchitis
110. Epiglottitis
111. Epilepsy
112. Epistaxis
113. Essential or secondary hypertension
114. Essential tremor
115. Extradural haemorrhage
116. Febrile convulsion
117. Fibroadenoma
118. Fibroids
119. Fibromyalgia
120. Fibrotic lung disease
121. Folliculitis
122. Gallstones and biliary colic
123. Gangrene
124. Gastric cancer
125. Gastrointestinal perforation
126. Gastro-oesophageal reflux disease
127. Gonorrhoea
128. Haemochromatosis
129. Haemoglobinopathies
130. Haemophilia
131. Haemorrhoids
132. Head lice
133. Henoch-Schonlein purpura
134. Hepatitis
135. Hernias
136. Herpes simplex virus
137. Hiatus hernia
138. Hospital acquired infections
139. Human immunodeficiency virus
140. Human papilloma virus infection
141. Hypercalcaemia of malignancy
142. Hyperlipidemia
143. Hyperosmolar hyperglycaemic state
144. Hyperparathyroidism
145. Hyperthermia and hypothermia
146. Hypoglycaemia
147. Hypoparathyroidism
148. Hyposplenism/splenectomy
149. Hypothyroidism
150. Idiopathic arthritis
151. Impetigo
152. Infectious colitis
153. Infectious diarrhoea
154. Infectious mononucleosis
155. Infective endocarditis
156. Infective keratitis
157. Inflammatory bowel disease
158. Influenza
159. Intestinal ischaemia
160. Intestinal obstruction and ileus
161. Intussusception
162. Iritis
163. Irritable bowel syndrome
164. Ischaemic heart disease
165. Kawasaki disease
166. Leukaemia
167. Liver failure
168. Lower limb fractures
169. Lower limb soft tissue injury
170. Lower respiratory tract infection
171. Lung cancer
172. Lyme disease
173. Lymphoma
174. Macular degeneration
175. Malabsorption
176. Malaria
177. Malignant melanoma
178. Malnutrition
179. Measles
180. Ménière's disease
181. Meningitis
182. Menopause
183. Mesenteric adenitis
184. Metastatic disease
185. Migraine
186. Mitral valve disease
187. Motor neurone disease
188. Multi-organ dysfunction syndrome
189. Multiple myeloma
190. Multiple sclerosis
191. Mumps
192. Muscular dystrophies
193. Myasthenia gravis
194. Myeloproliferative disorders
195. Myocardial infarction
196. Myocarditis
197. Necrotising enterocolitis
198. Necrotising fasciitis
199. Nephrotic syndrome
200. Non-accidental injury
201. Notifiable diseases
202. Obesity
203. Obesity and pregnancy
204. Obstructive sleep apnoea
205. Occupational lung disease
206. Oesophageal cancer
207. Optic neuritis
208. Osteoarthritis
209. Osteomalacia
210. Osteomyelitis
211. Osteoporosis
212. Otitis externa
213. Otitis media
214. Ovarian cancer
215. Pancreatic cancer
216. Pancytopenia
217. Parkinson's disease
218. Pathological fracture
219. Patient on anti-coagulant therapy
220. Patient on anti-platelet therapy
221. Pelvic inflammatory disease
222. Peptic ulcer disease and gastritis
223. Perianal abscesses and fistulae
224. Pericardial disease
225. Periorbital and orbital cellulitis
226. Peripheral nerve injuries/palsies
227. Peripheral vascular disease
228. Peritonitis
229. Personality disorder
230. Pituitary tumours
231. Placenta praevia
232. Placental abruption
233. Pneumonia
234. Pneumothorax
235. Polycythaemia
236. Polymyalgia rheumatica
237. Postpartum haemorrhage
238. Pre-eclampsia, gestational hypertension
239. Pressure sores
240. Prostate cancer
241. Psoriasis
242. Pulmonary embolism
243. Pulmonary hypertension
244. Pyloric stenosis
245. Radiculopathies
246. Raised intracranial pressure
247. Reactive arthritis
248. Respiratory arrest
249. Respiratory failure
250. Retinal detachment
251. Rheumatoid arthritis
252. Rhinosinusitis
253. Right heart valve disease
254. Rubella
255. Sarcoidosis
256. Scabies
257. Schizophrenia
258. Scleritis
259. Self-harm
260. Sepsis
261. Septic arthritis
262. Sickle cell disease
263. Somatisation
264. Spinal cord compression
265. Spinal cord injury
266. Spinal fracture
267. Squamous cell carcinoma
268. Stroke
269. Subarachnoid haemorrhage
270. Subdural haemorrhage
271. Substance use disorder
272. Surgical site infection
273. Syphilis
274. Systemic lupus erythematosus
275. Tension headache
276. Termination of pregnancy
277. Testicular cancer
278. Testicular torsion
279. Thyroid eye disease
280. Thyroid nodules
281. Thyrotoxicosis
282. Tonsillitis
283. Toxic shock syndrome
284. Transfusion reactions
285. Transient ischaemic attacks
286. Trichomonas vaginalis
287. Trigeminal neuralgia
288. Tuberculosis
289. Unstable angina
290. Upper limb fractures
291. Upper limb soft tissue injury
292. Upper respiratory tract infection
293. Urinary incontinence
294. Urinary tract calculi
295. Urinary tract infection
296. Urticaria
297. Uveitis
298. Varicella zoster
299. Varicose veins
300. Vasa praevia
301. Vasovagal syncope
302. Venous ulcers
303. Viral exanthema
304. Viral gastroenteritis
305. Viral hepatitides
306. Visual field defects
307. Vitamin B12 and/or folate deficiency
308. Volvulus
309. VTE in pregnancy and puerperium
310. Wernicke's encephalopathy
311. Whooping cough"""
        st.code(condition_list, language=None)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask Claude something..."):
    # Check if API key is provided
    if not st.session_state.api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
        st.stop()
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display assistant typing indicator
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            # Initialize Anthropic client
            client = anthropic.Anthropic(api_key=st.session_state.api_key)
            
            # Format messages for the API
            messages = [
                {"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages
            ]
            
            # Call the Claude API
            response = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=1024,
                temperature=0.7,
                system=st.session_state.system_prompt,
                messages=messages
            )
            
            # Display Claude's response
            message_placeholder.markdown(response.content[0].text)
            
            # Add Claude's response to chat history
            st.session_state.messages.append(
                {"role": "assistant", "content": response.content[0].text}
            )
            
        except Exception as e:
            message_placeholder.error(f"Error: {str(e)}")