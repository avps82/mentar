---
type: Mentar Visual Scaffold
title: "Faces, Edges and Corners of Solid Shapes"
description: "Visual scaffold for counting the faces, edges and corners of 3D shapes."
tags: [mathematics, year3, visual-scaffold]
subject: mathematics
topic_keywords: [3d shapes, 3d shape]
timestamp: "2026-08-22T00:00:00Z"
---

When writing or explaining this question, use this visual structure:

```key
solid              faces  edges  corners
cube, cuboid         6     12      8
triangular prism     5      9      6
square pyramid       5      8      5
cylinder             3      2      0
cone                 2      1      1
sphere               1      0      0
faces:   count the top, the bottom, then the ones around the side
corners: count the top face's, then the bottom face's
         (a pyramid's top is a single point; a sphere has none)
check (flat-faced solids): corners - edges + faces = 2
```

**Guidelines for the question text:**
- Name the solid ("a cube"), never ask about "a 3D shape" in general.
- Corners you cannot see still count: a drawn cube shows 7 of its 8.
- The top/bottom/around-the-side procedure counts FACES. Applying it to
  corners double-counts and yields 12 instead of 8.
- Neither procedure is cube-only: a triangular prism is 3 corners on top and 3
  on the bottom (6), a square pyramid 4 and a single apex (5). Saying "4 on top,
  4 on the bottom" is the same mistake one line up, wearing a different hat --
  and this node's own first question is about a triangular prism.
- Curved solids follow the table's convention; prefer cube, cuboid, prism
  or pyramid, where every source agrees on the number.
