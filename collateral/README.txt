VSHARK — CUSTOMER COLLATERAL
============================

Ready to send
  VShark-Presentation.pdf           17-slide company presentation (16:9)
  VShark-Presentation.pptx          same deck as an editable PowerPoint file
  VShark-Brochure-Services.pdf      2-page A4 brochure — services first, scanners in short
  VShark-Brochure-Scanners.pdf      2-page A4 brochure — scanners for sale, services in short
  VShark-Portfolio-Reverse-Engineering.pdf   A4 portfolio — every 3D scanning & reverse engineering project
  VShark-Portfolio-Inspection.pdf            A4 portfolio — every 3D scanning & inspection (metrology) project
  (print double-sided or email)

  The portfolios pick their projects from the website data: a project tagged "reverse-engineering"
  or "digital-metrology" in data/site.json appears automatically after a rebuild.

To present live
  Open presentation.html in Chrome/Edge.
  Arrow keys / click = next or previous slide, F = full screen.

To update
  Content comes from data/site.json (the same file the website uses), so service,
  industry, product and contact changes flow through automatically.
  After editing, run from the repo root:

      python collateral/build_collateral.py

  This rewrites presentation.html, both brochure-*.html files, both portfolio-*.html files, the JPEG copies in assets/,
  all three PDFs (needs Pillow and Microsoft Edge or Google Chrome) and the
  PowerPoint file (needs Node.js; first time only:  npm install --prefix collateral).
  PowerPoint layout lives in build_pptx.js; fonts are Century Gothic + Calibri,
  which come with Microsoft Office, so the deck looks the same on any PC.
  Layout/colours: deck.css (presentation) and brochure.css (both brochures).
  Text that is not on the website (about copy, process steps, testimonials,
  which portfolio images to show, scanner "why buy from us" points) is near the
  top of build_collateral.py and above scanners_brochure().
