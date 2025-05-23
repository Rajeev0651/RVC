import os
from collections import OrderedDict

import torch


def extract(ckpt):
    a = ckpt["model"]
    opt = OrderedDict()
    opt["weight"] = {}
    for key in a.keys():
        if "enc_q" in key:
            continue
        opt["weight"][key] = a[key]
    return opt


def model_blender(name, path1, path2, ratio):
    try:
        message = f"Model {path1} and {path2} are merged with alpha {ratio}."
        ckpt1 = torch.load(path1, map_location="cpu", weights_only=False)
        ckpt2 = torch.load(path2, map_location="cpu", weights_only=False)

        if ckpt1["sr"] != ckpt2["sr"]:
            return "The sample rates of the two models are not the same."

        cfg = ckpt1["config"]
        cfg_f0 = ckpt1["f0"]
        cfg_version = ckpt1["version"]
        cfg_sr = ckpt1["sr"]

        if "model" in ckpt1:
            ckpt1 = extract(ckpt1)
        else:
            ckpt1 = ckpt1["weight"]
        if "model" in ckpt2:
            ckpt2 = extract(ckpt2)
        else:
            ckpt2 = ckpt2["weight"]

        if sorted(list(ckpt1.keys())) != sorted(list(ckpt2.keys())):
            return "Fail to merge the models. The model architectures are not the same."

        opt = OrderedDict()
        opt["weight"] = {}
        for key in ckpt1.keys():
            if key == "emb_g.weight" and ckpt1[key].shape != ckpt2[key].shape:
                min_shape0 = min(ckpt1[key].shape[0], ckpt2[key].shape[0])
                opt["weight"][key] = (
                    ratio * (ckpt1[key][:min_shape0].float())
                    + (1 - ratio) * (ckpt2[key][:min_shape0].float())
                ).half()
            else:
                opt["weight"][key] = (
                    ratio * (ckpt1[key].float()) + (1 - ratio) * (ckpt2[key].float())
                ).half()

        opt["config"] = cfg
        opt["sr"] = cfg_sr
        opt["f0"] = cfg_f0
        opt["version"] = cfg_version
        opt["info"] = message

        torch.save(opt, os.path.join("logs", f"{name}.pth"))
        print(message)
        return message, os.path.join("logs", f"{name}.pth")
    except Exception as error:
        print(f"An error occurred blending the models: {error}")
        return error
