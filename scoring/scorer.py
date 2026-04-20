#!/usr/bin/env python3
"""
AuditorSEC Scoring Engine v0.1
UA Defensive Cyber Ecosystem Audit Framework
https://github.com/AuditorSEC-Initiative/auditor-sec
"""
import yaml
import json
from pathlib import Path

# Вагові коефіцієнти
WEIGHTS_EXPERT = {
    "academic_depth": 0.20,
    "practical_impact": 0.25,
    "educational_activity": 0.20,
    "regulatory_audit_fit": 0.20,
    "ua_context_relevance": 0.15,
}

WEIGHTS_MEDIA = {
    "defensive_ethical_focus": 0.25,
    "content_quality_freshness": 0.20,
    "career_educational_value": 0.20,
    "practical_community_value": 0.20,
    "noise_clickbait_penalty": 0.15,
}

WEIGHTS_TECH = {
    "technology_readiness": 0.25,
    "rd_vs_production_ratio": 0.20,
    "ua_applicability": 0.30,
    "regulatory_compatibility": 0.25,
}


def fit_label_expert(score: float) -> str:
    if score >= 3.5:
        return "high"
    elif score >= 2.0:
        return "medium"
    return "low"


def media_tier(score: float) -> str:
    if score > 4.0:
        return "tier1"
    elif score >= 2.5:
        return "tier2"
    return "tier3"


def tech_tier(score: float) -> str:
    if score >= 3.5:
        return "pilot_ready"
    elif score >= 2.0:
        return "research"
    return "research"


def score_profile(profile: dict) -> dict:
    obj_type = profile.get("type", "expert")
    metrics = profile.get("metrics_raw", {})

    if obj_type == "expert":
        weights = WEIGHTS_EXPERT
    elif obj_type == "media":
        weights = WEIGHTS_MEDIA
    elif obj_type == "technology":
        weights = WEIGHTS_TECH
    else:
        weights = WEIGHTS_EXPERT

    weighted = sum(
        metrics.get(k, 0) * w
        for k, w in weights.items()
    )
    weighted = round(weighted, 2)

    output = {"weighted_score": weighted}

    if obj_type == "expert":
        output["audit_fit"] = fit_label_expert(weighted)
        output["regulatory_fit"] = fit_label_expert(
            metrics.get("regulatory_audit_fit", 0))
        output["educational_value"] = fit_label_expert(
            metrics.get("educational_activity", 0))
        output["ua_relevance"] = fit_label_expert(
            metrics.get("ua_context_relevance", 0))
    elif obj_type == "media":
        output["media_tier"] = media_tier(weighted)
        output["recommended_for"] = profile.get("recommended_for", [])
    elif obj_type == "technology":
        output["tech_tier"] = tech_tier(weighted)
        output["recommended_use_cases"] = [
            uc.get("name") for uc in profile.get("use_cases_ua", [])]

    return output


def process_directory(path: Path, label: str):
    results = []
    for profile_path in sorted(path.glob("*.yaml")):
        if ".scored" in profile_path.name:
            continue
        with open(profile_path, encoding="utf-8") as f:
            profile = yaml.safe_load(f)

        output = score_profile(profile)
        profile["output"] = output

        out_path = profile_path.with_suffix(".scored.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)

        score = output["weighted_score"]
        fit = output.get("audit_fit") or output.get(
            "media_tier") or output.get("tech_tier")
        name = profile.get("name", profile_path.stem)
        print(f"  [{label}] {name}: {score}/5.00 → {fit}")
        results.append({"name": name, "score": score, "fit": fit})
    return results


def main():
    print("=" * 50)
    print("AuditorSEC Scoring Engine v0.1")
    print("=" * 50)

    base = Path("profiles")
    all_results = []

    for folder, label in [
        ("experts", "EXPERT"),
        ("media", "MEDIA"),
        ("technologies", "TECH"),
    ]:
        folder_path = base / folder
        if folder_path.exists():
            print(f"\nСкоринг {label}:")
            results = process_directory(folder_path, label)
            all_results.extend(results)

    print("\n" + "=" * 50)
    print(f"Загалом оброблено: {len(all_results)} профілів")
    print("Scored .json файли збережено поруч з профілями.")


if __name__ == "__main__":
    main()
