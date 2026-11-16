---
slug: stl-is-not-cad-brief-checklist
order: 21
title: STL Is Not CAD: The Scan-to-CAD Brief Checklist
title_tag: STL Is Not CAD: Scan-to-CAD Brief Checklist | VShark
description: Brief a scan-to-CAD job in ten lines: scan format, datums, tolerances, mating parts, deliverables, NDA. What to send so the STEP is right first time.
category: Reverse Engineering
tags: STL is not CAD, scan to CAD brief, STL to STEP, reverse engineering checklist
featured: blog-images/stl-is-not-cad-brief-checklist/3d-scan-data-car-wheel-on-screen.webp
service: /services/reverse-engineering
---

An STL is a mesh of triangles that copies the surface of a scanned part. It has no real faces, holes or dimensions, so it is not CAD and cannot be edited like CAD. To turn it into a STEP model you can use, send a short brief with ten items: the scan files, units and scale, a datum frame, purpose and fidelity, which features must be exact, tolerances and deviation target, material and process, mating parts, the file formats you want, and NDA, IP and deadline. The checklist below explains each one and what goes wrong when it is missing. We scan and do scan-to-CAD in India and the UAE.

![3D scan data of a car wheel shown on a computer screen](blog-images/stl-is-not-cad-brief-checklist/3d-scan-data-car-wheel-on-screen.webp)

*Last reviewed: November 2026*

### Why is an STL not CAD?
A mesh records where the surface was, including wear, casting texture, scan noise and holes in the data. CAD records what the part is meant to be: planes, cylinders, radii and a feature tree. Going from one to the other is a rebuild, not a conversion. Someone has to decide which surface is a plane, which hole is round and where the datum is. Your brief is how you make those decisions yours instead of a guess. For the file types themselves, read [what files you get from a 3D scan](/blog/3d-scan-file-formats?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s66&utm_content=blog-file-formats).

### The ten-item brief checklist
Copy this into an email. Short answers are fine; "not known" is a valid answer and tells us what to measure.

| # | Item | What to send | If it is missing |
|---|---|---|---|
| 1 | Scan files | The full-resolution mesh (STL, PLY or OBJ) plus any alignment or marker data. Do not decimate or smooth it. Say which scanner and what scan noise to expect. | A thinned mesh loses small radii and edges, and the rebuild drifts. |
| 2 | Units and scale | mm or inch, and one known dimension (a caliper reading of a long length). | A mesh has no built-in units; a part can arrive 25.4 times off. |
| 3 | Datum frame | Which face is the mounting face, which axis is the slide or rotation axis, and which way is up. Photo with arrows is enough. | We pick an orientation from the scan and you re-align later. |
| 4 | Purpose and fidelity | Replica of the as-scanned part, or design intent (round values, symmetric, flat)? Is it a mount or adapter (the interface is exact, the rest is an envelope), a full replica, or the packaging volume only? | Effort goes into the wrong surfaces, and either wear is copied or intent is invented. |
| 5 | Features that must be exact | List the holes, bores, seats, threads and mating faces that must be parametric and exact. The rest can follow the mesh. | Everything gets the same effort, or critical interfaces are modelled as loosely as cosmetic skin. |
| 6 | Tolerances and deviation target | The tolerance on the critical features, and the average and worst-case deviation you accept between the model and the scan. | Neither side can say whether the model passes. |
| 7 | Material and process | Cast, machined, moulded, printed or fabricated? Raw or finished surface? Wall thickness, draft, shrink allowance. | Casting draft is modelled as tilt, or a single-sided scan gets a wall thickness that is a guess. |
| 8 | Mating parts | Your CAD or drawings of the parts it fits to, or at least their key dimensions. | We take mating dimensions from the scan instead of your authority, and fit checks fail. |
| 9 | Deliverables and software | STEP as the base, plus IGES or Parasolid if needed, and the software that opens it (for example SolidWorks or Fusion). Say if you also want the STL, a deviation report PDF, or a script. Neutral formats open in these tools; native files are not supplied as standard. | You get a format your system reads badly. |
| 10 | NDA, IP and deadline | Whether an NDA is needed (say so before sending data), who owns the finished model, the date you need it, and how many revision rounds you expect. | Data waits until paperwork is agreed, and the date slips. |

### How should I send the scan data?
Send the original scan, not a version cleaned up for viewing. Keep marker or alignment files if you used them. Say if the scan is single-sided (no wall visible, for example the outside of a cover only), because a single-sided scan has no wall, so wall thickness becomes a design value and not a measurement. Say which areas were hard to scan (shiny, dark, deep). A few overview photos of the real part help us identify features the mesh hides.

### Which features should be parametric and which can follow the mesh?
Make a short two-column list: "exact" and "follow the scan". Exact usually means holes that take fasteners, bores and shafts, sealing and locating faces, and anything that touches another part. Follow-the-scan usually means cosmetic skin, organic curves and casting texture. This split decides the cost of the job and how well the model behaves when you edit it. Say so if you expect to change dimensions later, because that needs a proper feature tree.

### What tolerance and deviation target should I ask for?
Ask for a deviation check between the finished model and your scan, and agree the targets before work starts. They depend on the scan noise and the process, so they are set per job. As a guide, we work to a tight target on the critical interface (average around a quarter of a millimetre, with the worst 5 percent under about 0.8 mm). On raw castings the rest of the part typically matches the scan less closely (median around 0.4 mm, worst 5 percent around 1.6 mm on four casting jobs), because raw cast surfaces and scan noise limit what any model can match. These are typical results, set per job, not a guarantee. A deviation colour map shows where the model sits inside or outside the scan, and a PDF report can be requested with the model.

### What about bowed, worn or damaged parts?
Say whether you want the part as scanned or as intended. A long part bowed by about a millimetre may be real or may be scan error. In that case we can supply a bowed and a straight version and ask you to choose. Holes the scan cannot show and hidden pocket ceilings are guessed, and we list them so you can check them with calipers.

### What do you send back?
A STEP model as the base, other neutral formats on request, a deviation check, and a short list of what was simplified and what to verify on the real part. The STL is supplied on request. Quote on request; turnaround is set per part after we see the data.

### Where do we work?
VShark Solutions does 3D scanning and scan-to-CAD in India and the UAE. If you already own a scanner and want the CAD done, see [reverse engineering services in India](/reverse-engineering-services-india?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s66&utm_content=hub-re) and [rebuilding a spare part with no drawing](/spare-part-no-drawing-reverse-engineering?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s66&utm_content=spare-part). For the modelling steps, read [scan to CAD in SolidWorks](/blog/scan-to-cad-in-solidworks?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s66&utm_content=blog-scan-to-cad). For inspection against a nominal model, see [CMM inspection services](/cmm-inspection-services?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s66&utm_content=cmm-page).

### FAQ

**Is an STL file CAD?**
No. An STL is a mesh of triangles that copies the scanned surface. It has no editable faces or dimensions. CAD formats such as STEP carry real geometry that you can change.

**Can you convert my STL to STEP?**
Yes, but not with one click. The mesh is used as a reference and the part is rebuilt as a CAD model, with the exact features you list modelled as parametric geometry. Send the brief checklist with the file.

**What do I need to send for a scan-to-CAD quote?**
The full-resolution scan, units and one known dimension, a datum description, the purpose of the model, the features that must be exact, tolerances, material and process, mating parts, the formats you want and any NDA. A photo of the real part helps.

**What file formats do you deliver?**
STEP as the base, with IGES, Parasolid and other neutral formats on request. These open in SolidWorks, Fusion and other CAD software. Native files of one CAD system are not supplied as standard.

**How accurate will the CAD be against my scan?**
It depends on the scan noise, the surface and the process. We agree a deviation target for the critical features and the rest of the part before starting, and check the model against your scan.

**Do I need to send my own CAD of the mating parts?**
It is best if you do. Mating dimensions from your CAD or drawing are more reliable than dimensions measured from a scan.

**Can you sign an NDA before I send the data?**
Tell us in your brief that you need one.

**Where are you based?**
We scan and model from India and the UAE and work with clients abroad. Send a photo or the file and your brief through the [contact page](/contact?service=reverse-engineering&utm_source=website&utm_medium=seo&utm_campaign=2026-11-s66&utm_content=cta) and we will reply with a quote.

### Contact
Have a scan and need CAD? Send the brief above. [Get a quote](/contact?service=reverse-engineering&utm_source=website&utm_medium=seo&utm_campaign=2026-11-s66&utm_content=cta-end) or email info@vsharksolutions.com.

VShark Solutions is a distributor of JINUOSH.

