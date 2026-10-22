/* =========================================================
   Hero — laser scan → deliverable.
   01 3D Scanning        : live point cloud with sweeping laser
   02 Reverse Engineering: scan of a flange → solid CAD + edges
   03 Scan to BIM        : building scan → slabs / columns / glazing
   04 Class A Surfacing  : car-body scan → zebra-striped surface
   Each modelled scene is sampled into the point cloud; after the
   points settle, the laser sweeps upward and the solid model is
   revealed exactly where the laser has passed (clipping plane).
   Exposes window.VSharkHero = { start(), onShape(cb), ... }
   ========================================================= */
(function () {
  const canvas = document.getElementById('heroCanvas');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const api = { start() {}, onShape() {}, ok: false };
  window.VSharkHero = api;
  if (!canvas || !window.THREE) return;

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
  } catch (e) { return; }
  api.ok = true;

  const isMobile = window.matchMedia('(max-width: 760px)').matches;
  const N = isMobile ? 9000 : 18000;
  const PR = Math.min(window.devicePixelRatio || 1, 2);
  renderer.setPixelRatio(PR);
  renderer.setClearColor(0x000000, 0);
  renderer.localClippingEnabled = true;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
  camera.position.set(0, 0.4, 9);

  scene.add(new THREE.HemisphereLight(0xffffff, 0xaab2b9, 0.95));
  const keyLight = new THREE.DirectionalLight(0xffffff, 0.85);
  keyLight.position.set(3, 6, 5);
  scene.add(keyLight);
  const rimLight = new THREE.DirectionalLight(0xffe3e7, 0.35);
  rimLight.position.set(-5, 2, -4);
  scene.add(rimLight);

  const rand = Math.random;
  const TAU = Math.PI * 2;
  const V3 = THREE.Vector3;
  const COL = { slate: 0x616b6f, steel: 0x828b94, maroon: 0x991b2e, ink: 0x1c2125, metal: 0xd5dade, white: 0xeef0f2 };

  /* =========================================================
     Helpers
     ========================================================= */

  // Area-weighted random points on every mesh surface under `root`
  // (coordinates relative to root's parent, i.e. the shared group).
  function sampleSurface(root, n) {
    root.updateMatrixWorld(true);
    const tris = [];
    const cum = [];
    let total = 0;
    const a = new V3(), b = new V3(), c = new V3(), ab = new V3(), ac = new V3();
    root.traverse((o) => {
      if (!o.isMesh || o.userData.noSample) return;
      const g = o.geometry.index ? o.geometry.toNonIndexed() : o.geometry;
      const p = g.attributes.position;
      const w = o.userData.sampleWeight || 1;
      for (let i = 0; i < p.count; i += 3) {
        a.fromBufferAttribute(p, i).applyMatrix4(o.matrixWorld);
        b.fromBufferAttribute(p, i + 1).applyMatrix4(o.matrixWorld);
        c.fromBufferAttribute(p, i + 2).applyMatrix4(o.matrixWorld);
        const area = ab.subVectors(b, a).cross(ac.subVectors(c, a)).length() * 0.5 * w;
        if (area <= 1e-9) continue;
        total += area;
        cum.push(total);
        tris.push(a.x, a.y, a.z, b.x, b.y, b.z, c.x, c.y, c.z);
      }
    });
    const out = new Float32Array(n * 3);
    let minY = Infinity, maxY = -Infinity;
    for (let i = 0; i < n; i++) {
      const r = rand() * total;
      let lo = 0, hi = cum.length - 1;
      while (lo < hi) { const mid = (lo + hi) >> 1; if (cum[mid] < r) lo = mid + 1; else hi = mid; }
      const k = lo * 9;
      let u = rand(), v = rand();
      if (u + v > 1) { u = 1 - u; v = 1 - v; }
      const noise = 0.008; // a little scanner noise
      for (let d = 0; d < 3; d++) {
        out[i * 3 + d] = tris[k + d] + u * (tris[k + 3 + d] - tris[k + d]) + v * (tris[k + 6 + d] - tris[k + d]) + (rand() - 0.5) * noise;
      }
      minY = Math.min(minY, out[i * 3 + 1]);
      maxY = Math.max(maxY, out[i * 3 + 1]);
    }
    return { data: out, minY, maxY };
  }

  const std = (color, extra) => new THREE.MeshStandardMaterial(Object.assign({ color, roughness: 0.5, metalness: 0.15, side: THREE.DoubleSide }, extra));

  /* =========================================================
     01 — 3D Scanning: freeform object → triangulated scan mesh
     ========================================================= */
  function buildScanMesh() {
    const root = new THREE.Group();
    const P = 2, Q = 3, s = 0.62;
    class KnotCurve extends THREE.Curve {
      getPoint(u, target = new V3()) {
        const t = u * TAU;
        const r = Math.cos(Q * t) + 2.2;
        return target.set(r * Math.cos(P * t) * s, -Math.sin(Q * t) * 1.1 * s, r * Math.sin(P * t) * s);
      }
    }
    // deliberately coarse, flat-shaded triangles: reads as a raw scan mesh (STL)
    const geo = new THREE.TubeGeometry(new KnotCurve(), isMobile ? 120 : 170, 0.52 * s, isMobile ? 10 : 13, true);
    const surface = new THREE.Mesh(geo, std(0xcfd4d8, { flatShading: true, roughness: 0.62, metalness: 0.1 }));
    const wire = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: COL.slate, wireframe: true, transparent: true, opacity: 0.32 }));
    wire.userData.noSample = true;
    root.add(surface, wire);
    return { root, spin: true };
  }

  /* =========================================================
     02 — Reverse Engineering: pipe flange → CAD solid
     ========================================================= */
  function buildFlange() {
    const root = new THREE.Group();

    const shape = new THREE.Shape();
    shape.absarc(0, 0, 1.5, 0, TAU, false);
    const bore = new THREE.Path(); bore.absarc(0, 0, 0.5, 0, TAU, true); shape.holes.push(bore);
    for (let k = 0; k < 6; k++) {
      const an = (k / 6) * TAU + Math.PI / 6;
      const h = new THREE.Path(); h.absarc(Math.cos(an) * 1.1, Math.sin(an) * 1.1, 0.15, 0, TAU, true);
      shape.holes.push(h);
    }
    const plateGeo = new THREE.ExtrudeGeometry(shape, { depth: 0.3, bevelEnabled: true, bevelThickness: 0.035, bevelSize: 0.035, bevelSegments: 2, curveSegments: 56 });
    plateGeo.rotateX(-Math.PI / 2);

    const hubGeo = new THREE.LatheGeometry([
      new THREE.Vector2(0.5, 0), new THREE.Vector2(0.86, 0), new THREE.Vector2(0.86, 0.42),
      new THREE.Vector2(0.74, 0.62), new THREE.Vector2(0.5, 0.62), new THREE.Vector2(0.5, 0),
    ], 72);
    hubGeo.translate(0, 0.32, 0);

    const metal = std(COL.metal, { metalness: 0.45, roughness: 0.38 });
    const plate = new THREE.Mesh(plateGeo, metal);
    const hub = new THREE.Mesh(hubGeo, metal);
    root.add(plate, hub);

    // CAD feature edges (revealed by the laser together with the solid)
    const edgeMat = new THREE.LineBasicMaterial({ color: COL.ink, transparent: true, opacity: 0.8 });
    [plateGeo, hubGeo].forEach((g) => root.add(new THREE.LineSegments(new THREE.EdgesGeometry(g, 30), edgeMat)));

    root.rotation.set(0.62, 0, 0.12);
    root.position.y = -0.35;
    root.scale.setScalar(1.18);

    return { root };
  }

  /* =========================================================
     03 — Scan to BIM: as-built point cloud → BIM elements
     ========================================================= */
  function buildBIM() {
    const root = new THREE.Group();
    const floors = 4, fh = 0.62, W = 2.6, D = 1.7, t = 0.07;
    const slabMat = std(COL.slate, { roughness: 0.7 });
    const colMat = std(COL.maroon, { roughness: 0.55 });
    const coreMat = std(COL.white, { roughness: 0.8 });
    const glassMat = new THREE.MeshStandardMaterial({ color: 0x9db0be, transparent: true, opacity: 0.32, roughness: 0.08, metalness: 0.3, depthWrite: false, side: THREE.DoubleSide });
    const mullionMat = new THREE.LineBasicMaterial({ color: COL.slate, transparent: true, opacity: 0.6 });

    for (let f = 0; f <= floors; f++) {
      const slab = new THREE.Mesh(new THREE.BoxGeometry(W + 0.18, t, D + 0.18), slabMat);
      slab.position.y = f * fh;
      root.add(slab);
      if (f === floors) break;

      const y = f * fh + fh / 2 + t / 2;
      const h = fh - t;
      [-W / 2, -W / 6, W / 6, W / 2].forEach((x) => [-D / 2, D / 2].forEach((z) => {
        const col = new THREE.Mesh(new THREE.BoxGeometry(0.08, h, 0.08), colMat);
        col.position.set(x, y, z);
        root.add(col);
      }));

      // curtain-wall glazing on four sides
      [[W, 0.015, 0, D / 2], [W, 0.015, 0, -D / 2], [0.015, D, W / 2, 0], [0.015, D, -W / 2, 0]].forEach(([w, d, x, z]) => {
        const g = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), glassMat);
        g.position.set(x, y, z);
        g.userData.sampleWeight = 0.35;
        root.add(g);
      });

      // mullions
      const pts = [];
      for (let i = 0; i <= 8; i++) {
        const x = -W / 2 + (i / 8) * W;
        pts.push(x, y - h / 2, D / 2, x, y + h / 2, D / 2, x, y - h / 2, -D / 2, x, y + h / 2, -D / 2);
      }
      for (let i = 0; i <= 5; i++) {
        const z = -D / 2 + (i / 5) * D;
        pts.push(W / 2, y - h / 2, z, W / 2, y + h / 2, z, -W / 2, y - h / 2, z, -W / 2, y + h / 2, z);
      }
      const mg = new THREE.BufferGeometry();
      mg.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
      root.add(new THREE.LineSegments(mg, mullionMat));
    }

    const coreH = floors * fh + 0.38;
    const core = new THREE.Mesh(new THREE.BoxGeometry(0.62, coreH, 0.62), coreMat);
    core.position.set(0.55, coreH / 2, -0.15);
    root.add(core);

    root.position.y = -(floors * fh) / 2 - 0.1;
    root.rotation.y = 0.5;
    root.scale.setScalar(0.98);
    return { root };
  }

  /* =========================================================
     04 — Class A Surfacing: airliner with zebra analysis
     ========================================================= */
  function zebraMaterial() {
    const m = new THREE.ShaderMaterial({
      uniforms: { uTime: { value: 0 }, uOpacity: { value: 1 } },
      side: THREE.DoubleSide,
      transparent: true,
      clipping: true,
      vertexShader: /* glsl */`
        #include <clipping_planes_pars_vertex>
        varying vec3 vN;
        varying vec3 vV;
        void main() {
          vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
          vN = normalize(normalMatrix * normal);
          vV = -mvPosition.xyz;
          gl_Position = projectionMatrix * mvPosition;
          #include <clipping_planes_vertex>
        }`,
      fragmentShader: /* glsl */`
        #include <clipping_planes_pars_fragment>
        uniform float uTime, uOpacity;
        varying vec3 vN;
        varying vec3 vV;
        void main() {
          #include <clipping_planes_fragment>
          vec3 n = normalize(vN);
          if (!gl_FrontFacing) n = -n;
          vec3 v = normalize(vV);
          vec3 r = reflect(-v, n);
          float s = r.y * 5.5 + r.x * 1.2 + uTime * 0.3;
          float band = abs(fract(s) - 0.5) * 2.0;
          float stripe = smoothstep(0.42, 0.58, band);
          vec3 col = mix(vec3(0.11, 0.13, 0.145), vec3(0.97, 0.975, 0.98), stripe);
          float fres = pow(1.0 - max(dot(n, v), 0.0), 3.0);
          col = mix(col, vec3(0.6, 0.106, 0.18), fres * 0.35);
          gl_FragColor = vec4(col, uOpacity);
        }`,
    });
    m.userData.base = 1;
    return m;
  }

  // Swept, tapered lifting surface with a symmetric NACA 00xx section.
  // Local axes: chord runs toward -x from the leading edge, span along +z, thickness along y.
  function liftingSurface({ root, tip, span, sweep, dihedral = 0, thick = 0.12 }) {
    const NX = 22, NZ = isMobile ? 10 : 16;
    const pos = [], idx = [];
    const naca = (u) => 5 * thick * (0.2969 * Math.sqrt(u) - 0.126 * u - 0.3516 * u * u + 0.2843 * u ** 3 - 0.1036 * u ** 4);
    [1, -1].forEach((side) => {
      const base = pos.length / 3;
      for (let j = 0; j <= NZ; j++) {
        const t = j / NZ;
        const c = root + (tip - root) * t;
        const le = -sweep * t;
        for (let i = 0; i <= NX; i++) {
          const u = (1 - Math.cos((i / NX) * Math.PI)) / 2; // cluster points at the leading edge
          pos.push(le - u * c, dihedral * t + side * naca(u) * c, span * t);
        }
      }
      for (let j = 0; j < NZ; j++) {
        for (let i = 0; i < NX; i++) {
          const a = base + j * (NX + 1) + i, b = a + NX + 1;
          if (side > 0) idx.push(a, a + 1, b, b, a + 1, b + 1);
          else idx.push(a, b, a + 1, b, b + 1, a + 1);
        }
      }
    });
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setIndex(idx);
    g.computeVertexNormals();
    return g;
  }

  function buildAirplane() {
    const root = new THREE.Group();
    const skin = zebraMaterial();
    const L = 4.5, R = 0.3;

    // fuselage: lathe profile (radius, station from tail 0 → nose L)
    const prof = [];
    const NS = 64;
    for (let i = 0; i <= NS; i++) {
      const h = (i / NS) * L;
      let r = R;
      if (h < 1.25) r = R * Math.pow(Math.max(h, 0.02) / 1.25, 0.75);                       // tail cone
      if (h > L - 0.75) r = R * Math.sqrt(Math.max(0, 1 - ((h - (L - 0.75)) / 0.75) ** 2)); // nose
      prof.push(new THREE.Vector2(Math.max(r, 0.004), h));
    }
    const fus = new THREE.LatheGeometry(prof, isMobile ? 28 : 40);
    fus.rotateZ(-Math.PI / 2); // lathe axis Y → X (nose toward +x)
    fus.translate(-L / 2, 0, 0);
    // upswept tail
    const fp = fus.attributes.position;
    for (let i = 0; i < fp.count; i++) {
      const x = fp.getX(i), k = (-L / 2 + 1.25 - x) / 1.25;
      if (k > 0) fp.setY(i, fp.getY(i) + 0.24 * k ** 1.6);
    }
    fus.computeVertexNormals();
    root.add(new THREE.Mesh(fus, skin));

    [1, -1].forEach((s) => {
      // main wings (low wing, swept, dihedral)
      const w = new THREE.Mesh(liftingSurface({ root: 1.15, tip: 0.32, span: 2.1, sweep: 0.95, dihedral: 0.2, thick: 0.13 }), skin);
      w.position.set(0.4, -0.13, 0);
      w.scale.z = s;
      root.add(w);

      // horizontal stabilisers
      const st = new THREE.Mesh(liftingSurface({ root: 0.52, tip: 0.2, span: 0.82, sweep: 0.42, dihedral: 0.06, thick: 0.1 }), skin);
      st.position.set(-1.62, 0.2, 0);
      st.scale.z = s;
      root.add(st);

      // engine nacelle under each wing
      const nac = new THREE.LatheGeometry([
        new THREE.Vector2(0.1, 0), new THREE.Vector2(0.15, 0.08), new THREE.Vector2(0.16, 0.3),
        new THREE.Vector2(0.15, 0.55), new THREE.Vector2(0.13, 0.62), new THREE.Vector2(0.12, 0.6),
      ], 28);
      nac.rotateZ(Math.PI / 2); // axis Y → -X: intake (station 0) faces forward
      const n = new THREE.Mesh(nac, skin);
      n.position.set(0.72, -0.21, s * 0.78);
      root.add(n);

      // pylon joining nacelle to wing
      const py = new THREE.Mesh(new THREE.BoxGeometry(0.46, 0.12, 0.035), skin);
      py.position.set(0.42, -0.08, s * 0.78);
      py.userData.sampleWeight = 0.4;
      root.add(py);
    });

    // vertical fin
    const fin = new THREE.Mesh(liftingSurface({ root: 0.85, tip: 0.3, span: 0.9, sweep: 0.62, thick: 0.1 }), skin);
    fin.rotation.x = -Math.PI / 2; // span +z → +y
    fin.position.set(-1.38, 0.22, 0);
    root.add(fin);

    root.rotation.set(0.42, -0.55, 0.08); // three-quarter view from above
    root.position.y = 0.05;
    root.scale.setScalar(1.02);
    return { root, tick: (t) => { skin.uniforms.uTime.value = t; } };
  }

  /* =========================================================
     Scene registry
     ========================================================= */
  const group = new THREE.Group();
  scene.add(group);

  function modelScene(name, word, built) {
    const { root } = built;
    const { data, minY, maxY } = sampleSurface(root, N);
    const plane = new THREE.Plane(new V3(0, 1, 0), -1e3); // keeps world y >= -constant (hidden by default)
    const mats = [];
    root.traverse((o) => {
      if (!o.material) return;
      const m = o.material;
      if (mats.includes(m)) return;
      m.transparent = true;
      m.clippingPlanes = [plane];
      if (m.userData.base === undefined) m.userData.base = m.opacity;
      mats.push(m);
    });
    root.visible = false;
    group.add(root);
    return Object.assign({ name, word, data, minY, maxY, plane, mats }, built);
  }

  function setOpacity(s, k) {
    s.mats.forEach((m) => {
      if (m.uniforms && m.uniforms.uOpacity) m.uniforms.uOpacity.value = m.userData.base * k;
      else m.opacity = m.userData.base * k;
    });
  }

  const shapes = [
    modelScene('POINTS → MESH', '3D Scanning Solutions', buildScanMesh()),
    modelScene('MESH → CAD', 'Reverse Engineering', buildFlange()),
    modelScene('POINTS → BIM', 'Scan to BIM Modelling', buildBIM()),
    modelScene('ZEBRA · G2 SURFACE', 'Class A Surfacing', buildAirplane()),
  ];

  /* =========================================================
     Point cloud
     ========================================================= */
  const geo = new THREE.BufferGeometry();
  const rnd = new Float32Array(N);
  for (let i = 0; i < N; i++) rnd[i] = rand();
  geo.setAttribute('position', new THREE.BufferAttribute(shapes[0].data.slice(), 3));
  geo.setAttribute('aTo', new THREE.BufferAttribute(shapes[0].data.slice(), 3));
  geo.setAttribute('aRand', new THREE.BufferAttribute(rnd, 1));

  const uniforms = {
    uTime: { value: 0 },
    uSweepUp: { value: -1e3 },                      // height the up-stroke has reached (points form below it)
    uReveal: { value: 1e3 },                        // solid model exists above this height
    uHasSolid: { value: 0 },                        // current scene has a solid model
    uOldVis: { value: 1 },                          // visibility of points not yet re-formed
    uScan: { value: 0 },
    uSize: { value: isMobile ? 34 : 30 },
    uPR: { value: PR },
    uFade: { value: 0 },
    uBase: { value: new THREE.Color('#4f585d') },  // logo slate, deepened for contrast on light bg
    uHot: { value: new THREE.Color('#991b2e') },   // logo maroon
  };

  const mat = new THREE.ShaderMaterial({
    uniforms,
    transparent: true,
    depthWrite: false,
    vertexShader: /* glsl */`
      uniform float uTime, uScan, uSize, uPR, uSweepUp, uReveal, uHasSolid, uOldVis;
      attribute vec3 aTo;
      attribute float aRand;
      varying float vGlow;
      varying float vAlpha;
      varying float vVis;
      varying float vM;
      void main() {
        // each point re-forms when the rising laser reaches its target height
        vec4 tw = modelMatrix * vec4(aTo, 1.0);
        float m = clamp((uSweepUp - tw.y - aRand * 0.12) / 0.3, 0.0, 1.0);
        m = m * m * (3.0 - 2.0 * m);
        vec3 p = mix(position, aTo, m);
        float k = sin(m * 3.14159);
        p += k * vec3(
          sin(aRand * 40.0 + uTime * 1.1),
          cos(aRand * 31.0 + uTime * 1.3),
          sin(aRand * 17.0 + uTime * 0.7)) * 0.25;
        p += 0.012 * vec3(sin(uTime * 0.9 + aRand * 20.0), cos(uTime * 0.7 + aRand * 12.0), 0.0);
        vec4 wp = modelMatrix * vec4(p, 1.0);
        float d = wp.y - uScan;
        vGlow = exp(-d * d * 22.0);
        vec4 mv = viewMatrix * wp;
        gl_Position = projectionMatrix * mv;
        gl_PointSize = uSize * uPR * (0.55 + aRand * 0.7) * (1.0 + vGlow * 1.6) / -mv.z;
        vAlpha = 0.25 + 0.55 * aRand;
        // dim points where the solid model has already been revealed
        float solidHere = uHasSolid * step(uReveal, wp.y);
        vVis = mix(uOldVis, mix(1.0, 0.12, solidHere), m);
        vM = m;
      }`,
    fragmentShader: /* glsl */`
      uniform vec3 uBase, uHot;
      uniform float uFade;
      varying float vGlow;
      varying float vAlpha;
      varying float vVis;
      varying float vM;
      void main() {
        vec2 c = gl_PointCoord - 0.5;
        float r = length(c);
        if (r > 0.5) discard;
        float a = smoothstep(0.5, 0.0, r);
        vec3 col = mix(uBase, uHot, clamp(vGlow * 1.4, 0.0, 1.0));
        float vis = max(vVis, vGlow * 0.8 * vM);
        gl_FragColor = vec4(col, a * min(1.0, 0.3 + vAlpha * 0.6 + vGlow * 0.6) * vis * (1.0 - uFade));
      }`,
  });

  const points = new THREE.Points(geo, mat);
  points.renderOrder = 2; // after the solids, so hidden points stay hidden
  group.add(points);

  /* ---------- Laser scan plane ---------- */
  const scanGroup = new THREE.Group();
  const ringMat = new THREE.MeshBasicMaterial({ color: COL.maroon, transparent: true, opacity: 0.6, side: THREE.DoubleSide, depthWrite: false });
  const ring = new THREE.Mesh(new THREE.RingGeometry(2.9, 2.92, 128), ringMat);
  ring.rotation.x = -Math.PI / 2;
  scanGroup.add(ring);
  const discMat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, side: THREE.DoubleSide,
    uniforms: { uFade: uniforms.uFade },
    vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
    fragmentShader: `uniform float uFade; varying vec2 vUv; void main(){ float d = length(vUv - 0.5) * 2.0; float a = smoothstep(1.0, 0.0, d) * 0.10 + smoothstep(0.02, 0.0, abs(d - 0.98)) * 0.2; gl_FragColor = vec4(0.6, 0.106, 0.18, a * 0.7 * (1.0 - uFade)); }`,
  });
  const disc = new THREE.Mesh(new THREE.PlaneGeometry(5.9, 5.9), discMat);
  disc.rotation.x = -Math.PI / 2;
  disc.renderOrder = 3;
  scanGroup.add(disc);
  scene.add(scanGroup);

  /* ---------- Ambient dust ---------- */
  const DUST = isMobile ? 250 : 600;
  const dGeo = new THREE.BufferGeometry();
  const dPos = new Float32Array(DUST * 3);
  for (let i = 0; i < DUST; i++) {
    dPos[i * 3] = (rand() - 0.5) * 22;
    dPos[i * 3 + 1] = (rand() - 0.5) * 12;
    dPos[i * 3 + 2] = (rand() - 0.5) * 10 - 2;
  }
  dGeo.setAttribute('position', new THREE.BufferAttribute(dPos, 3));
  const dust = new THREE.Points(dGeo, new THREE.PointsMaterial({ color: COL.steel, size: 0.025, transparent: true, opacity: 0.45, depthWrite: false }));
  scene.add(dust);

  /* ---------- Layout ---------- */
  function resize() {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    // wide: object to the right of the headline; narrow: in the space above it
    const wide = w / h > 1.1;
    group.position.set(wide ? 1.9 : 0, wide ? 0.25 : 1.75, 0);
    scanGroup.position.x = group.position.x;
    const sc = wide ? 1 : Math.min(0.62, (w / h) * 1.0);
    group.scale.setScalar(sc);
    scanGroup.scale.setScalar(sc);
  }
  window.addEventListener('resize', resize);
  resize();

  /* ---------- Interaction ---------- */
  const mouse = { x: 0, y: 0, tx: 0, ty: 0 };
  window.addEventListener('pointermove', (e) => {
    mouse.tx = (e.clientX / window.innerWidth) * 2 - 1;
    mouse.ty = (e.clientY / window.innerHeight) * 2 - 1;
  }, { passive: true });

  const shapeCbs = [];
  api.onShape = (cb) => shapeCbs.push(cb);
  api.shapes = shapes;
  api.count = N;

  /* =========================================================
     Laser-driven sequence
     One pass = up stroke + down stroke, at one constant speed.
       Up   : the new scene's points form as the laser passes their
              height; the previous solid model is erased below it.
       Down : the current scene's solid model is revealed above it.
       Bottom of the pass → next scene. Every scene lasts one pass.
     ========================================================= */
  const STROKE = 3.2; // seconds per stroke (up or down)
  const RANGE = 1.9;  // laser travel above/below the model centre (group units)
  let current = 0;
  let prev = -1;
  let queued = null;
  let passT = 0;
  let started = false;

  function beginScene(i) {
    prev = current;
    current = i;
    const pos = geo.attributes.position.array;
    const tgt = geo.attributes.aTo.array;
    pos.set(tgt); // last scene's settled points become the new start positions
    tgt.set(shapes[i].data);
    geo.attributes.position.needsUpdate = true;
    geo.attributes.aTo.needsUpdate = true;
    const old = shapes[prev];
    uniforms.uOldVis.value = old && old.root ? 0.12 : 1;
    uniforms.uHasSolid.value = shapes[i].root ? 1 : 0;
    shapes.forEach((s, k) => { if (s.root) s.root.visible = k === i || k === prev; });
    shapeCbs.forEach((cb) => cb(i, shapes[i]));
  }

  // Visitor picks a service: the laser makes a quick return to the bottom
  // (REWIND s), then the chosen scene starts its normal constant-speed pass.
  const REWIND = 0.5;
  let rewind = null;
  let lastScanY = 0;
  api.select = (i) => {
    if (i < 0 || i >= shapes.length) return;
    if (reduceMotion) { if (i !== current) beginScene(i); return; }
    if (!started) { queued = i; return; }
    if (rewind) { rewind.target = i; return; }
    if (i === current) return;
    rewind = { from: lastScanY, t: 0, target: i, up: passT < STROKE, sweep: uniforms.uSweepUp.value };
  };
  api.goTo = api.select;
  // progress of the active scene's pass, 0 → 1 (drives the tab progress bar)
  api.progress = () => (rewind ? 0 : passT / (STROKE * 2));
  api.current = () => current;

  /* ---------- Visibility & scroll fade ---------- */
  let visible = true;
  const io = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; }, { threshold: 0 });
  io.observe(canvas);

  api.setScrollProgress = (p) => {
    uniforms.uFade.value = Math.min(1, p * 1.1);
    camera.position.z = 9 + p * 4;
    camera.position.y = 0.4 - p * 1.5;
  };

  /* ---------- HUD hooks ---------- */
  const hudX = document.getElementById('hudX');
  const hudY = document.getElementById('hudY');
  const hudScan = document.getElementById('hudScan');
  const fmt = (n) => (n >= 0 ? '+' : '') + n.toFixed(3);

  /* ---------- Loop ---------- */
  const clock = new THREE.Clock();
  let frame = 0;
  let yaw = 0;
  let t = 0;
  function tick() {
    requestAnimationFrame(tick);
    const dt = Math.min(0.05, clock.getDelta()); // pauses cleanly while off-screen
    if (!visible) return;
    t += dt;
    uniforms.uTime.value = t;

    mouse.x += (mouse.tx - mouse.x) * 0.05;
    mouse.y += (mouse.ty - mouse.y) * 0.05;

    const speed = reduceMotion ? 0 : 1;
    if (shapes[current].root && !shapes[current].spin) {
      // solid models: sway around the nearest "front" angle so the good side stays visible
      const front = Math.round(yaw / TAU) * TAU;
      const target = front + Math.sin(t * 0.35) * 0.55 * speed;
      yaw += (target - yaw) * Math.min(1, dt * 1.8);
    } else {
      yaw += dt * 0.18 * speed; // point cloud: continuous turntable
    }
    group.rotation.y = yaw + mouse.x * 0.7;
    group.rotation.x = mouse.y * 0.25 + 0.12;

    /* --- laser: constant-speed up/down pass --- */
    const bottom = group.position.y - RANGE * group.scale.y;
    const top = group.position.y + RANGE * group.scale.y;
    const cur = shapes[current];
    let scanY;

    if (rewind) {
      // quick return to the bottom, then start the chosen scene
      rewind.t += dt;
      const k = Math.min(1, rewind.t / REWIND);
      scanY = rewind.from + (bottom - rewind.from) * (k * k * (3 - 2 * k));
      if (!rewind.up) {
        // was revealing on the way down: keep revealing as the laser drops
        uniforms.uReveal.value = scanY;
        if (cur.root) cur.plane.constant = -scanY;
      }
      if (k >= 1) {
        const target = rewind.target;
        rewind = null;
        passT = 0;
        if (target !== current) beginScene(target);
      }
    } else {
      if (started && !reduceMotion) passT += dt;
      if (passT >= STROKE * 2) {
        passT -= STROKE * 2;
        const next = queued !== null ? queued : (current + 1) % shapes.length;
        queued = null;
        beginScene(next);
      }
      const up = passT < STROKE;
      const f = up ? passT / STROKE : 1 - (passT - STROKE) / STROKE; // 0 = bottom, 1 = top
      scanY = reduceMotion ? group.position.y : bottom + (top - bottom) * f;
      uniforms.uSweepUp.value = reduceMotion || !up ? 1e3 : scanY;
      uniforms.uReveal.value = reduceMotion ? -1e3 : up ? 1e3 : scanY;
      const c = shapes[current];
      const o = prev >= 0 && prev !== current ? shapes[prev] : null;
      if (c.root) c.plane.constant = reduceMotion ? 1e3 : up ? -1e3 : -scanY; // revealed above the laser on the way down
      if (o && o.root) {
        if (up && !reduceMotion) o.plane.constant = -scanY; // erased below the laser on the way up
        else o.root.visible = false;
      }
    }
    lastScanY = scanY;
    uniforms.uScan.value = scanY;
    scanGroup.position.y = scanY;
    ringMat.opacity = 0.6 * (1 - uniforms.uFade.value);

    shapes.forEach((s) => {
      if (!s.root || !s.root.visible) return;
      if (s.tick) s.tick(t);
      setOpacity(s, 1 - uniforms.uFade.value); // fade with the hero on scroll
    });

    dust.rotation.y = t * 0.01;
    dust.position.x = -mouse.x * 0.3;
    dust.position.y = mouse.y * 0.2;

    renderer.render(scene, camera);

    if (++frame % 4 === 0) {
      // live model rotation (keeps moving on touch screens, where there is no mouse)
      if (hudX) hudX.textContent = fmt(group.rotation.x);
      if (hudY) hudY.textContent = fmt(Math.atan2(Math.sin(group.rotation.y), Math.cos(group.rotation.y)));
      if (hudScan) hudScan.textContent = (scanY >= 0 ? '+' : '') + scanY.toFixed(2);
    }
  }

  api.start = () => {
    // intro: the first scan pass gathers a scattered cloud into the first object
    const pos = geo.attributes.position.array;
    for (let i = 0; i < N; i++) {
      const r = 2.5 + rand() * 2, th = rand() * TAU, ph = Math.acos(2 * rand() - 1);
      pos[i * 3] = r * Math.sin(ph) * Math.cos(th);
      pos[i * 3 + 1] = r * Math.cos(ph);
      pos[i * 3 + 2] = r * Math.sin(ph) * Math.sin(th);
    }
    geo.attributes.position.needsUpdate = true;
    uniforms.uOldVis.value = 0; // scattered points stay invisible until the laser reaches them
    uniforms.uHasSolid.value = shapes[0].root ? 1 : 0;
    if (shapes[0].root) shapes[0].root.visible = true;
    passT = 0;
    started = true;
    shapeCbs.forEach((cb) => cb(0, shapes[0]));
  };

  tick();
})();
