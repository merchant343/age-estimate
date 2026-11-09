"""Compare baseline and at most two preprocessing candidates on fixed data."""
from pathlib import Path
import csv, json, re
from PIL import Image, ImageOps
from transformers import pipeline

ROOT = Path(__file__).resolve().parents[1]; DATA = ROOT / "artifacts" / "synthetic_dataset"; OUT = ROOT / "artifacts" / "evaluation"
MODEL_ID = "nateraw/vit-age-classifier"

def predicted_mid(label):
    nums = [int(x) for x in re.findall(r"\d+", label.replace("–", "-"))]
    return (nums[0] + (nums[1] if len(nums) > 1 else nums[0] + 4)) / 2 if nums else 18.0

def mae(model, rows, transform):
    errors=[]
    for row in rows:
        image=Image.open(row["path"]).convert("RGB")
        out=model(transform(image))[0]
        errors.append(abs(predicted_mid(out["label"]) - float(row["age"])))
    return sum(errors)/len(errors)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with (DATA/"manifest.csv").open(encoding="utf-8") as f: rows=list(csv.DictReader(f))
    tune=[r for r in rows if r["split"] == "tune"]; final=[r for r in rows if r["split"] == "final"]
    model=pipeline("image-classification", model=MODEL_ID, device=-1)
    candidates=[("baseline", lambda x:x), ("autocontrast", ImageOps.autocontrast), ("equalize", ImageOps.equalize)]
    tune_scores=[{"name":n,"mae":mae(model,tune,fn)} for n,fn in candidates]
    best=min(tune_scores,key=lambda x:x["mae"])
    selected=next(fn for n,fn in candidates if n==best["name"])
    final_scores={"baseline_mae":mae(model,final,lambda x:x),"selected_mae":mae(model,final,selected),"selected":best["name"],"improved":best["mae"] < tune_scores[0]["mae"],"tune_count":len(tune),"final_count":len(final),"attempts":2,"model":MODEL_ID,"synthetic_only":True}
    result={"tuning":tune_scores,"final":final_scores,"warning":"Synthetic data validates the pipeline only; it does not establish real-world content-rating accuracy."}
    (OUT/"comparison.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))

if __name__ == "__main__": main()
