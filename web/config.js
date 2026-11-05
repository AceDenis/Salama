/* Salama Check-In: settings. Edit this file, nothing else, to connect your own database.
   BACKEND "demo"     = everything stays in this browser (for practice and training).
   BACKEND "supabase" = answers go to your database. Fill in the two Supabase values below. */
window.SALAMA_CONFIG = {
  BACKEND: "demo",
  SUPABASE_URL: "https://YOUR-PROJECT.supabase.co",
  SUPABASE_ANON_KEY: "YOUR-ANON-PUBLIC-KEY",

  STUDY_NAME: "Salama Check-In pilot (NDU-Kenya, Defence College of Health Sciences)",
  APP_VERSION: "1.1.0",
  PROTOCOL_VERSION: "P1.0",            // change this whenever you change a question or rule, and record it in the Change log

  // Unit and group codes shown in the app. They are group labels, never names of people.
  UNITS: [
    { code: "DCHS-STU", label: "DCHS student (enrolled)" },
    { code: "DCHS-APP", label: "DCHS applicant (not yet enrolled)" },
    { code: "UNIT-A",   label: "Pilot unit A (later phase)" },
    { code: "UNIT-B",   label: "Pilot unit B (later phase)" },
    { code: "OTHER",    label: "Other or not sure" }
  ],

  // false = interviewers and the selection panel see nothing. Set true ONLY if the ethics committee and DCHS governance approve the
  // colour look-up. It changes the wording shown to applicants. The database role "interviewer" must also be granted (04_make_staff.sql).
  INTERVIEWER_COLOUR: false,

  // Optional AI guide. Leave "" to use the on-phone guide only (nothing leaves the phone). To use an AI model, deploy
  // database/edge_ai_guide.ts as a Supabase Edge Function and paste its URL here. Do this only with ethics and data-protection approval:
  // what people type is sent to an AI provider outside the phone.
  // Phone number of the nurse call-back phone for the "No data or signal?" text card. Leave "" to hide it.
  NURSE_SMS: "+2547xxxxxxxx",   // placeholder: replace with the real nurse phone when the service is adopted
  AI_ENDPOINT: "",

  // Who can use this link. "student" = DCHS students and applicants only (default for this study).
  // Add "personnel", "family" or "informant" later if the study is extended.
  ROLES: ["student"],
  // true = the expert-input page (index.html?role=informant&form=delphi) works for the five-staff expert review, without showing that option to students.
  EXPERT_LINK: true,
  // Number of students you expect to take part. The monthly report uses it to show the participation rate. Leave 0 to hide it.
  EXPECTED_PARTICIPANTS: 0,

  // Shown to participants before they agree to take part (the "Your protections" card). Fill in after ethics approval.
  ETHICS_REF: "Ethics approval number: [to be added]",
  CONTACT_TEXT: "Supervisor and ethics committee contacts: [to be added]",

  // Referral and contact buttons shown under "Get help". Each can have tel, whatsapp (digits with country code) and sms.
  // Fill these in with your confirmed local contacts before go-live. hours and note are free text.
  REFERRALS: [
    { label: "DCHS student support office", note: "Placeholder number, to be updated when the service is adopted", hours: "Weekdays", value: "+2547xxxxxxxx", tel: "+2547xxxxxxxx", whatsapp: "", sms: "" },
    { label: "Chaplain", note: "Placeholder number, to be updated", value: "+2547xxxxxxxx", tel: "+2547xxxxxxxx", whatsapp: "" },
    { label: "Welfare officer", note: "Money, housing, family. Placeholder number, to be updated", value: "+2547xxxxxxxx", tel: "+2547xxxxxxxx", whatsapp: "" }
  ],

  // Shown on the call-back screen. Edit to match the real rota agreed with the hospital (see proposal section 3.4.4).
  COVER_NOTE: "A nurse takes requests from 07:00 to 21:00. If you need help outside those hours, use the numbers on the Get help page. Your request will be seen first when cover starts.",
  CALLBACK_HOURS_HIGH: 8,              // target for same-day requests
  CALLBACK_DAYS_ROUTINE: 7,            // target for routine requests

  // Switch off any question if ethics or legal review asks you to. Use the item id from docs/codebook.csv.
  // Example: DISABLED_ITEMS: ["fm_lost", "sec_id"]
  DISABLED_ITEMS: [],

  // Local contacts: fill in before go-live (nurse line, chaplain, welfare office, duty officer).
  LOCAL_CONTACTS: [
    { label: "Nurse on call (cover hours 07:00 to 21:00)", note: "Placeholder number, to be updated when the service is adopted", value: "+2547xxxxxxxx", tel: "+2547xxxxxxxx" },
    { label: "Duty medical officer (after hours)", note: "Placeholder number, to be updated", value: "+2547xxxxxxxx", tel: "+2547xxxxxxxx" }
  ],
  // National lines. Confirm every number and hours with the provider before go-live.
  NATIONAL_LINES: [
    { label: "Police and emergency", note: "Confirm before go-live", tel: "999", value: "999 or 112" },
    { label: "Gender violence helpline (free)", note: "Confirm before go-live", tel: "1195", value: "1195" },
    { label: "Kenya Red Cross counselling (free)", note: "Confirm before go-live", tel: "1199", value: "1199" },
    { label: "National mental health line", note: "Confirm before go-live", tel: "1190", value: "1190" },
    { label: "Befrienders Kenya", note: "Confirm before go-live", tel: "+254722178177", value: "+254 722 178 177" },
    { label: "Child helpline", note: "For anyone under 18. Confirm before go-live", tel: "116", value: "116" }
  ]
};
