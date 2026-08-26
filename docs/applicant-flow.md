# Applicant intake and program application

When an authenticated customer clicks **Apply** for a program and has no
applicant records, TurkDemy sends them directly to the applicant intake form.
There is no intermediate "create an applicant" empty state.

The intake asks whether the application is for **Myself** or **Someone else**.
For "Myself", known account identity/contact values are prefilled and remain
editable. Choosing "Someone else" clears those prefills.

Lead intake is intentionally permissive: applicant fields are optional so a
customer can express interest with incomplete information. Staff/agents can
collect and validate missing data later. The selected program is preserved in
`next_program` and is automatically attached to the newly created lead.

Customers who already manage one or more applicants still see the applicant
picker so they can choose which existing person the program belongs to.
