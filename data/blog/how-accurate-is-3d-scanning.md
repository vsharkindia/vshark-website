---
slug: how-accurate-is-3d-scanning
order: 7
title: How Accurate Is 3D Scanning? Precision, Accuracy and Tolerances Explained
title_tag: How Accurate Is 3D Scanning? Precision vs Accuracy | VShark
description: What 3D scanner accuracy specs really mean: precision, volumetric accuracy, resolution, and what affects real-world results when you scan and inspect parts.
category: 3D Scanning
tags: 3D scanning accuracy, scanner precision, volumetric accuracy, metrology, tolerances
featured: blog-images/how-accurate-is-3d-scanning/3d-scan-accuracy-deviation-colour-map.webp
service: /services/3d-scanning
---

![3D scan accuracy deviation colour map](blog-images/how-accurate-is-3d-scanning/3d-scan-accuracy-deviation-colour-map.webp)

"How accurate is your scanner?" is the first question almost every customer asks. It's a good question, but the honest answer is: **it depends on what you mean by accuracy, and on the part.** Here's a plain-English guide to the numbers on scanner spec sheets and what they mean for your project.

### Four numbers, four different things

**1. Precision (or accuracy) — e.g. 0.020 mm**
How closely the scanner measures a feature within a **single, small measurement area**. It's the best-case figure, often measured on calibrated artefacts. For example, the Vertex3D and Vertex3D Pro handheld scanners list 0.020 mm precision.

**2. Volumetric accuracy — e.g. 0.015 mm + 0.035 mm/m**
How error grows as the part gets **bigger**. When you scan a large part, small errors add up as the scanner moves around it. The formula means a base accuracy plus an extra amount for every metre of part size. For a 2 m part, that example spec gives roughly 0.015 + (0.035 × 2) = **0.085 mm**.

**3. Volumetric accuracy with photogrammetry**
For large parts, a **photogrammetry** step first measures a framework of reference targets very accurately; the scan is then locked to that framework. This reduces error growth on big objects.

**4. Resolution — e.g. 0.01 mm**
The **smallest point spacing** the scanner can capture. Higher resolution captures finer detail (text, knurling, small fillets), but resolution is **not** accuracy. A scan can be very detailed and still slightly out of size.

### What affects real-world accuracy
Spec sheets describe ideal conditions. On real projects, accuracy also depends on:
- **Part size:** larger parts mean more accumulated error, unless photogrammetry or tracking is used
- **Surface finish:** shiny, dark or transparent surfaces scatter or absorb light; blue-laser scanners handle many of these well, and a light matte spray helps on the hardest cases
- **Alignment and targets:** good reference-marker placement keeps scans stable
- **Temperature and stability:** parts and scanners expand and contract; metrology work needs stable conditions
- **Calibration:** scanners should be calibrated regularly
- **Operator skill:** scan strategy matters as much as hardware

![Reference targets placed on a car body before 3D scanning](blog-images/how-accurate-is-3d-scanning/reference-targets-placed-on-a-car-body-before-3d-scanning.webp)

![Scan to CAD overlay of a safety helmet shell](blog-images/how-accurate-is-3d-scanning/scan-to-cad-overlay-of-a-safety-helmet-shell.webp)

### How we measure our own results
On every reverse engineering and inspection job we compare data in a measurable way:
- **Scan to CAD:** the deviation between the final CAD and the scan, shown as a colour map and statistics
- **Known features:** checking measured features against calipers, gauges or CMM values where available

For example, on a cast transmission housing, the median deviation between scan and nominal CAD was about **0.24 mm**. A figure like this is mostly **casting variation** in the part plus the chosen alignment, not scanner error, and it is exactly the kind of insight 3D inspection is meant to reveal.

![Scan to CAD overlay of a steering wheel armature](blog-images/how-accurate-is-3d-scanning/scan-to-cad-overlay-of-a-steering-wheel-armature.webp)

### Matching accuracy to your tolerance
A useful rule of thumb from metrology: your measurement system should be **several times more accurate** than the tolerance you're checking. A common target is a 1:10 ratio, though 1:4 to 1:5 is often accepted in practice.

| Your tolerance | Is handheld 3D scanning suitable? |
|---|---|
| ±0.5 mm (castings, mouldings, sheet metal) | Yes, comfortably |
| ±0.1 mm (machined parts, precision mouldings) | Usually, with a good setup |
| ±0.01–0.02 mm (bearing seats, precision fits) | Use a CMM for those features; scan the rest |

### Ask the right question
Instead of "How accurate is the scanner?", ask: **"Can you measure my part, at this size, to this tolerance, and show me the proof?"** A good scanning partner will explain the setup and give you a report showing the result.

### 3D scanning in India and the UAE
VShark Solutions uses high-accuracy blue-laser scanning for reverse engineering and inspection, from **Coimbatore** and for clients across the **UAE**. Learn more about our [3D scanning service](/services/3d-scanning) or [digital metrology](/services/digital-metrology).

### FAQ

**What accuracy can I expect for my part?**
It depends on size, surface and setup. Share the part size and tolerance, and we'll tell you what's achievable and how we'll verify it.

**Do shiny or black parts reduce accuracy?**
They can be harder to scan. Blue-laser scanners handle many such surfaces well, and a light, removable matte spray is used when needed.

**Is a higher-resolution scan more accurate?**
Not necessarily. Resolution captures finer detail; accuracy is how close the measurements are to the true size. Both matter, but they are different.
