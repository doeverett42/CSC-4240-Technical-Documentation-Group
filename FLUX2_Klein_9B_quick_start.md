# FLUX.2 Klein 9B ComfyUI quick start

This workflow targets **FLUX.2 Klein 9B**, whose text encoder is **Qwen3 8B**. This is likely the “FLUX 2 8B” setup you meant.

## Install the models

Place the files like this:

```text
ComfyUI/
└─ models/
   ├─ diffusion_models/
   │  └─ flux-2-klein-base-9b-fp8.safetensors
   ├─ text_encoders/
   │  └─ qwen_3_8b_fp8mixed.safetensors
   └─ vae/
      └─ full_encoder_small_decoder.safetensors
```

Update ComfyUI before importing the workflow because FLUX.2 uses newer core nodes, including `Flux2Scheduler` and `EmptyFlux2LatentImage`.

## Import and run

1. Open ComfyUI.
2. Drag `flux2_klein_9b_learning_workflow.json` onto the canvas, or use **Workflow → Open**.
3. Confirm the three loader nodes show your installed model filenames.
4. Edit the positive prompt.
5. Click **Queue**.

## Good baseline

| Control | Starting value | What to learn |
|---|---:|---|
| Seed | 42, fixed | Keep fixed while comparing settings |
| Width × height | 1024 × 1024 | Use multiples of 16 |
| Steps | 20 | Compare 12, 20, and 28 |
| CFG | 5.0 | Compare 3.5, 5.0, and 6.5 |
| Sampler | Euler | Establish a baseline before comparing others |
| Batch size | 1 | Increase only when memory allows |

Change one setting at a time with the seed fixed. This makes differences attributable to that setting. When you want fresh compositions, change the seed control from **fixed** to **randomize**.

## Base versus distilled model

The included graph selects `flux-2-klein-base-9b-fp8.safetensors`, which is better for learning full sampler behavior. The distilled `flux-2-klein-9b-fp8.safetensors` is designed for very low step counts; if you switch to it, start around 4 steps and do not expect base-model settings to transfer directly.

## Troubleshooting

- **Red/missing nodes:** update ComfyUI to a current release.
- **Model not in dropdown:** verify its folder, filename, and then refresh/restart ComfyUI.
- **Out of memory:** try 768×768, close other GPU-heavy apps, and keep batch size at 1.
- **Washed-out or overcooked image:** reduce CFG before adding steps.
- **Slow first run:** loading the 9B model and 8B text encoder is substantial; subsequent runs are usually faster if they remain loaded.
