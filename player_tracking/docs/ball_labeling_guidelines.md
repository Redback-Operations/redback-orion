# Project Orion Ball Labeling Guidelines

## Purpose

These guidelines define how to annotate the active AFL match ball for the
Project Orion T2 ball-detection pilot.

The goal is to create consistent YOLO object-detection annotations that can be
used to train and evaluate a dedicated ball detector.

## Class definition

This is a ball-only dataset with one class:

| Class ID | Class name | Definition |
|---|---|---|
| `0` | `BALL` | The active match ball currently in play |

The existing Orion all-classes model uses `BALL = 7`. That mapping does not
apply to this separate one-class dataset. If these annotations are later merged
into the all-classes dataset, the class IDs must be remapped and verified.

## Core annotation rules

### 1. Label only the active match ball

Label the ball currently involved in play.

Do not label:

- spare balls beside the boundary;
- ball-shaped signs or logos;
- equipment or markers;
- reflections;
- shadows;
- other red or oval objects that are not the active ball.

### 2. Use one box per active ball

An image should normally contain:

- one `BALL` bounding box when the active ball is visible; or
- no bounding box when the active ball is not visible.

Never draw duplicate or overlapping boxes around the same ball.

### 3. Draw a tight bounding box

The box should contain the complete visible ball with only a very small margin.

Do not unnecessarily include:

- surrounding grass;
- the ball's shadow;
- a player's hand;
- a player's clothing;
- nearby field markings.

Use a normal axis-aligned rectangle. Do not use a rotated box, polygon or
segmentation mask.

### 4. Exclude the ball's shadow

The ball and its shadow may be close together, especially when the ball is
airborne. The shadow is not part of the ball and must remain outside the box.

### 5. Label a ball held by a player

Label the active ball when a player is holding it.

Keep the box focused on the ball even when it touches or overlaps a hand,
arm or uniform.

### 6. Handle partial occlusion consistently

If the ball is partly hidden but can still be identified confidently, draw the
box around its visible or clearly apparent boundary.

If most of the ball is hidden and its position or size would need to be
guessed, do not draw a box. Record the image as an uncertain case for review.

### 7. Handle motion blur consistently

If the moving ball is still clearly identifiable, include the complete visible
blurred ball shape in the box.

Do not include a separate shadow or long background trail. If the object could
reasonably be a boot, hand, field marking or another object, treat the case as
uncertain instead of guessing.

### 8. Handle distant balls carefully

Zoom in before making a decision.

Label a distant ball only when:

- it can be identified confidently as the active match ball; and
- its approximate visible boundary can be located.

If it remains an indistinct group of pixels after zooming, record it as
uncertain.

### 9. Use the exact class name

Use only:

```text
BALL
```

Do not introduce alternative class names such as `FOOTBALL`, `ACTIVE_BALL`,
`BALL_BLURRY` or `BALL_HELD`.

The different ball situations should remain examples of the same `BALL` class.

### 10. Do not guess

Annotation consistency is more important than forcing a label into every
image.

If the active ball cannot be identified confidently:

1. leave the image without a ball box;
2. record why it is unclear;
3. request review if necessary.

## Decision guide

| Situation | Action |
|---|---|
| Active ball clearly airborne | Label it |
| Active ball clearly on the ground | Label it |
| Active ball clearly held by a player | Label it |
| Ball partly hidden but still identifiable | Label the visible/apparent ball boundary |
| Ball mostly hidden and position is uncertain | Do not guess; record for review |
| Ball visible but affected by motion blur | Label the complete identifiable blurred shape |
| Tiny object cannot be confirmed after zooming | Do not label; record for review |
| Spare balls visible near the boundary | Do not label them |
| Ball-shaped sign, logo, marker or shadow | Do not label it |
| Active ball not visible anywhere in the frame | Use as a negative example |

## Negative examples

The dataset should include some images where no active ball is visible. These
help the detector learn when not to produce a ball detection.

For a YOLO dataset, a negative image should have a matching empty `.txt` label
file during dataset preparation.

Negative examples may include:

- play where the ball is completely hidden;
- wide field views with no visible ball;
- stationary spare balls near the boundary but no visible active ball;
- red uniforms, signs or equipment that could cause false detections.

## Image selection guidelines

The dataset should contain varied examples:

- airborne balls;
- held balls;
- ground-level balls;
- distant balls;
- motion-blurred balls;
- partially occluded balls;
- different camera angles and zoom levels;
- different matches, teams, lighting and field areas;
- images with no visible active ball.

Avoid using too many nearly identical consecutive frames. Similar adjacent
frames can make the dataset appear larger without adding much useful variety.

Training, validation and test footage must be separated carefully. Frames from
the same short sequence should not be divided across those sets because that
would make evaluation results misleading.

## Annotation workflow

For each image:

1. View the full image to understand the play.
2. Identify which object is the active match ball.
3. Zoom in to confirm the object and its boundary.
4. Select the `BALL` class.
5. Draw one tight box around the active ball.
6. Check that the shadow and unnecessary background are excluded.
7. Zoom out and confirm the selected object makes sense in context.
8. Submit the annotation or record the image as uncertain.

## Quality review checklist

Before accepting an annotation, confirm:

- [ ] The selected object is the active match ball.
- [ ] There is only one box around the ball.
- [ ] The box contains the complete visible ball.
- [ ] The box is tight and has only a small margin.
- [ ] The shadow is excluded.
- [ ] Spare balls and ball-like objects are not labelled.
- [ ] The class name is exactly `BALL`.
- [ ] The decision follows the same rules as the other images.

## Uncertain-case record

Record difficult cases using a table like this:

| Image | Issue | Decision | Review needed |
|---|---|---|---|
| Example image name | Ball mostly hidden behind player | Left unlabelled | Yes |

Common issues include:

- severe occlusion;
- heavy motion blur;
- very small or distant objects;
- confusion between the active ball and a spare ball;
- confusion with red clothing, signage or field objects.

## Pilot review requirement

Label and review a small pilot batch before expanding the dataset.

For the first review, record:

- number of images;
- number of ball boxes;
- number of negative examples;
- number of uncertain cases;
- corrections requested;
- final decisions and reasons.

Do not begin a large annotation batch until the pilot rules and examples have
been reviewed for consistency.
