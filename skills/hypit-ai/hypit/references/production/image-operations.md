# Preparing generated images

Read this when a generated or supplied image needs to be combined, corrected, resized or cropped
before it becomes a model reference or a Track item. [Image direction](../playbooks/craft/image-direction.md)
owns what the image should communicate; [spatial layout](spatial.md) owns Canvas, Frame and fit.

An image operation publishes another ordinary image Output. The resulting image can feed Seedance,
a Visual Clip, another image operation, or any compatible project component. The operation belongs
in Source when that transformation is part of the reproducible production relationship.

## Flatten a fixed still-image arrangement

Image Compose has one narrow job: preserve a deliberately rigid two-dimensional arrangement of
existing still images and publish it as one PNG. A comparison board, contact sheet or intentionally
hard-edged collage can need exactly that operation.

Declare the Canvas and every rectangular destination explicitly:

```svml
<import as="space" from="@hypit/spatial@1"/>
<import as="image" from="@hypit/image-operations@1"/>

<space:Canvas id="comparison-canvas" width="2048" height="1024"/>
<space:Frame id="before-panel" within={comparison-canvas.bounds}
  left="0%" top="0%" right="50%" bottom="100%"/>
<space:Frame id="after-panel" within={comparison-canvas.bounds}
  left="50%" top="0%" right="100%" bottom="100%"/>

<image:Compose id="comparison" canvas={comparison-canvas.canvas} background="#EEEAE2FF">
  <image:Layer source={before.image} frame={before-panel} fit="contain"/>
  <image:Layer source={after.image} frame={after-panel} fit="contain"/>
</image:Compose>
```

Child order is paint order. Each Layer keeps the source image, destination Frame, fit and optional
opacity explicit. `fit` accepts `contain`, `cover` and `stretch`; `interpolation` selects the raster
resampling filter. The background is `#RRGGBBAA`, so `#00000000` is transparent. The published
`{comparison.image}` is one flattened PNG rather than a Track.

Image Compose does not understand people, objects or camera space. It cannot reconcile perspective,
depth, lighting, subject scale, background continuity or a natural seam. When several references
should become one coherent camera image, direct the image model to create that image. When the layers
must remain independently timed, clipped, moved or revised in the video, keep them in Tracks and Film.

## Apply a reusable correction program

Image Transform separates the ordered correction choices from the image they act on:

```svml
<import as="image" from="@hypit/image-operations@1"/>

<image:Program id="delivery-crop">
  <image:Crop x="0" y="0" width="1080" height="1920" unit="pixel"/>
  <image:Resize width="1080" height="1920" fit="cover"/>
  <image:Encode format="png"/>
</image:Program>

<image:Transform id="prepared-shot" source={shot.image} program={delivery-crop}/>
```

Operations run in written order. A Program is authored data and produces no pixels until a
Transform applies it. Crop, resize, rotate, flip, denoise, color, sharpen, blur, alpha handling and
encoding are available; use `hypit vocabulary @hypit/image-operations --tag Program` for their
installed fields and limits. `{prepared-shot.image}` is the transformed image.

Use correction to express a known production choice. A prompt problem remains owned by the image
direction and its Prompt Kit; a different composition remains owned by the shot or reference
relationship.

## Keep operation and Clip use distinct

Composing or correcting image bytes changes the reusable image itself. A Visual Clip places
an image in a Frame for a Window and may animate that occurrence. Choose the former when several
downstream consumers should receive the same prepared pixels; choose the latter when the change
belongs only to how this video presents the image.

Inspect the selected package vocabulary before using optional fields. The examples above provide the
stable Source shapes; Endpoint choice, credentials and execution capacity remain Runtime concerns.
