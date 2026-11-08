---
slug: scan-to-cad-in-solidworks
order: 14
title: Scan to CAD in SolidWorks: How a Mesh Becomes an Editable Model
title_tag: Scan to CAD in SolidWorks: Mesh to Editable Model | VShark
description: How a 3D scan becomes editable CAD in SolidWorks or your CAD software: sections, surfaces, deviation check, STEP or Parasolid, and when a mesh is enough.
category: Reverse Engineering
tags: scan to CAD, SolidWorks, STEP, mesh to CAD, reverse engineering, deviation analysis
featured: blog-images/scan-to-cad-in-solidworks/reverse-engineered-cad-model-of-a-motorcycle-engine-crankcase.webp
service: /services/reverse-engineering
---

![Reverse-engineered CAD model of a motorcycle engine crankcase](blog-images/scan-to-cad-in-solidworks/reverse-engineered-cad-model-of-a-motorcycle-engine-crankcase.webp)

*Last reviewed: November 2026*

This article goes deep on the modelling step. For the full reverse engineering overview, read [what is reverse engineering](/blog/what-is-reverse-engineering?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s38&utm_content=blog-whatis-re).

### What is the difference between a scan and a CAD model?
A scan is a mesh: a very large number of small triangles that copy the surface of the part, including wear, casting texture and damage. You can measure it and compare it, but you cannot easily change a hole diameter, add a fillet or send it to a CNC programmer. A CAD model is built from real faces, sketches and features, so you can edit a dimension and the part updates. Scan to CAD is the work of rebuilding the second from the first.

### How does a scan become an editable model in SolidWorks?
The steps below are the usual order. Your CAD software may use different menu names, and the SolidWorks terms are used here only as a common example.

**1. Check and clean the mesh.** Before any modelling, the scan is checked for holes, noise and double surfaces, and cleaned where needed. A poor mesh gives a poor model, so this step comes first. The scanner exports a mesh such as STL (the Vertex scanners export STL, PLY, ASC and TXT).

**2. Set up the coordinate system.** The mesh is aligned to a sensible origin and axes, usually from the main flat faces, the axes of cylinders or the way the part sits in its assembly. This decides how every later sketch and feature lines up.

**3. Choose the modelling approach.** Different areas of one part can need different treatment:
- **Prismatic and machined areas:** planes, cylinders and cones are fitted to the mesh and the model follows design intent, with clean dimensions instead of the scatter of the scan.
- **Freeform areas:** smooth surfaces are fitted closely to the scan, "as-is", for body panels, ergonomic shapes and blades.
- **Hybrid:** machined features to design intent and freeform areas surfaced to the scan. Most real parts are hybrid.

**4. Fit sections and primitives to the mesh.** Section sketches are cut through the mesh and used as the basis of the features. Planes, cylinders and other simple shapes are fitted to the matching areas of the scan. In SolidWorks terms, these become the sketches that drive extrudes, revolves and lofts.

**5. Build the features and surfaces.** The features are built in order, much as a designer would model the part from scratch: base shape, holes, ribs, fillets. Freeform areas are surfaced and trimmed together with the solid features. A parametric rebuild keeps the dimensions editable, so you can change a hole size or a wall later. How far a job goes toward fully parametric depends on the part and what you need.

**6. Decide what to correct.** A scan records wear and damage. The engineer decides what is the real design and what is wear, then models the intended shape. This is why a worn spare can be rebuilt as a clean part, and why you tell us the purpose of the part before we start.

![Scan to CAD overlay of a motorcycle tubular frame](blog-images/scan-to-cad-in-solidworks/scan-to-cad-overlay-of-a-motorcycle-tubular-frame.webp)

**7. Run the deviation check.** The finished model is overlaid on the scan and the difference is shown as a colour map with statistics. This shows where the model follows the scan, and where a deliberate correction has moved it away. Areas outside what you expect are fixed and checked again. Where calipers, gauges or CMM values exist, known features are also checked against them.

**8. Deliver the files.** Neutral formats (see the next section), plus the STL scan on request.

### Which file formats do you get?
| Format | What it is | When to use it |
|---|---|---|
| STEP | Neutral solid and surface model | The usual choice to open the model in SolidWorks and most other CAD software |
| IGES | Older neutral format, mainly surfaces and curves | When the receiving software or vendor asks for it |
| Parasolid | Solid-modelling kernel format used by several CAD systems | When your CAD software reads it directly |
| STL scan (on request) | The mesh of the scan | Records, printing, visualisation, checking against the model |

We deliver STEP, IGES, Parasolid and other neutral formats that open in your CAD software. Native SolidWorks files are not part of the standard delivery. A neutral file carries the shapes and dimensions; it does not carry the original feature tree of another system, so tell us how you plan to edit the model and we will say what you will receive.

![3D scan data of a car wheel shown on a computer screen](blog-images/scan-to-cad-in-solidworks/3d-scan-data-car-wheel-on-screen.webp)

### Scan to CAD or mesh only: which do you need?
| What you want to do | Mesh only | Scan to CAD |
|---|---|---|
| Inspect a part against its nominal CAD | Yes | Not needed, but useful if no nominal CAD exists |
| Make a visual record or a render | Yes | No |
| 3D print a copy of the part | Often yes | Only if you want to change it |
| Change dimensions, add features, re-manufacture | No | Yes |
| Machine, mould or cast the part from a model | Rarely | Yes |
| Put the part into an assembly or a drawing | No | Yes |
| Rebuild a worn spare that has no drawing | No | Yes |

A mesh is faster to produce. A CAD model takes more engineering time but is the only version you can edit. If you are unsure, send the part and tell us what you will do with the file. We will say whether a mesh is enough. Quote on request.

### How do we work, and what do we need from you?
We scan the part with a handheld JINUOSH Vertex scanner, rebuild it in CAD, check the deviation and hand over the files. For the scan itself, see [handheld 3D scanner accuracy](/blog/handheld-3d-scanner-accuracy?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s38&utm_content=blog-handheld-accuracy) and [how to scan shiny and dark parts](/blog/scanning-shiny-reflective-parts?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s38&utm_content=blog-shiny). To get a useful model, tell us:
- what the model will be used for (manufacture, redesign, assembly, drawing)
- which dimensions or fits matter most
- which CAD software and file format you use
- whether wear or damage should be kept or corrected

![JINUOSH Vertex3D handheld blue laser 3D scanner, front view](blog-images/scan-to-cad-in-solidworks/jinuosh-vertex3d-handheld-blue-laser-3d-scanner-front.webp)

### Where do we do scan to CAD?
VShark Solutions works from Coimbatore, India, and serves clients in the UAE as a service area. We cover [3D scanning services in India](/3d-scanning-services-india?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s38&utm_content=hub-scanning), [reverse engineering services in India](/reverse-engineering-services-india?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s38&utm_content=hub-re) and [how we rebuild a spare part that has no drawing](/spare-part-no-drawing-reverse-engineering?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s38&utm_content=spare-part). By industry, see [automotive reverse engineering](/automotive-reverse-engineering-india?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s38&utm_content=automotive), [mould and die scanning](/mould-die-3d-scanning-india?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s38&utm_content=mould-die), [casting and foundry scanning](/casting-foundry-3d-scanning-india?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s38&utm_content=casting) and [industrial machinery spare parts](/industrial-machinery-spare-parts-3d-scanning-india?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s38&utm_content=machinery). To check a finished part against its CAD, see our [CMM inspection services in Coimbatore](/cmm-inspection-services?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s38&utm_content=cmm-page). If you only need a print, read [from 3D scan to 3D print](/blog/from-3d-scan-to-3d-print?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s38&utm_content=blog-print). Scanner enquiries are on the [JINUOSH Vertex 3D scanner page](/jinuosh-vertex-3d-scanner-india?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s38&utm_content=vertex-page). VShark is a distributor of JINUOSH.

### FAQ

**What is scan to CAD?**
It is the process of turning a 3D scan, which is a mesh of triangles, into an editable CAD model. The mesh is used as a reference, sections and surfaces are fitted to it, and the part is rebuilt as real faces and features that you can change.

**Can you convert an STL file to a SolidWorks model?**
Yes, but it is not a one-click conversion. An STL is a mesh, so the part is rebuilt in CAD using the mesh as a reference. We deliver the result as STEP, IGES or Parasolid, which open in SolidWorks and other CAD software.

**Which file formats do you deliver?**
STEP, IGES, Parasolid and other neutral formats that open in your CAD software. The STL scan is available on request. Native SolidWorks files are not part of the standard delivery.

**Will the CAD model match the scan exactly?**
Not point for point, and it should not. A model is made of clean faces and the scan contains wear and noise. We overlay the model on the scan and show the deviation as a colour map with statistics, so you can see where it matches and where a correction was made.

**Is the model fully parametric?**
It depends on the part and what you need. Machined features are rebuilt to design intent so that dimensions can be edited, and freeform areas are surfaced to follow the scan. Tell us how you plan to edit the model.

**When is a mesh enough, so I do not need CAD?**
For inspection against a nominal CAD, a visual record, a render or often a 3D print, the mesh is enough. You need CAD when you want to edit the part, machine, mould or cast it, or place it in an assembly.

**Can you rebuild a part that has no drawing?**
Yes. That is a common scan to CAD job. We scan the worn part, rebuild it, and correct the wear where you ask us to. See our page on [rebuilding a spare part with no drawing](/spare-part-no-drawing-reverse-engineering?utm_source=website&utm_medium=seo&utm_campaign=2026-11-s38&utm_content=faq-spare-part).

**Do you offer scan to CAD in the UAE?**
Yes, as a service area. VShark Solutions is based in Coimbatore, India. Send a photo of the part and what you need through the [contact page](/contact?service=reverse-engineering&utm_source=website&utm_medium=seo&utm_campaign=2026-11-s38&utm_content=cta) and we will say what is achievable. Quote on request.

### Contact
Have a part to rebuild? Send a photo or the scan and say which CAD software you use. [Get a quote](/contact?service=reverse-engineering&utm_source=website&utm_medium=seo&utm_campaign=2026-11-s38&utm_content=cta-end). Email: info@vsharksolutions.com.
