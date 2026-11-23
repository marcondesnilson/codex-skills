"""Conservative, non-duplicating USD reservation and usage accounting."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


USD_QUANTUM = Decimal("0.00000001")


def decimal_value(value, field="amount") -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
        raise ValueError(f"{field} must be a finite decimal number")
    try:
        result = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f"{field} must be a finite decimal number") from error
    if not result.is_finite():
        raise ValueError(f"{field} must be a finite decimal number")
    return result


def cost_number(value: Decimal) -> float:
    return float(value.quantize(USD_QUANTUM, rounding=ROUND_HALF_UP))


def estimate_cost_from_rates(
    text_tokens_upper_bound: int,
    image_input_tokens_upper_bound: int,
    output_tokens_upper_bound: int,
    pricing: dict,
    safety_factor: float,
    model: str,
    service_tier: str,
    image_output_tokens_upper_bound: int = 0,
) -> dict:
    rates = {
        name: decimal_value(pricing.get(name), f"pricing.{name}")
        for name in (
            "input_usd_per_million",
            "image_input_usd_per_million",
            "output_usd_per_million",
        )
    }
    image_output_rate = decimal_value(
        pricing.get("image_output_usd_per_million", pricing["output_usd_per_million"]),
        "pricing.image_output_usd_per_million",
    )
    input_cost = (
        Decimal(text_tokens_upper_bound) * rates["input_usd_per_million"]
        + Decimal(image_input_tokens_upper_bound) * rates["image_input_usd_per_million"]
    ) / Decimal(1_000_000)
    output_text_cost = Decimal(output_tokens_upper_bound) * rates["output_usd_per_million"] / Decimal(1_000_000)
    output_image_cost = Decimal(image_output_tokens_upper_bound) * image_output_rate / Decimal(1_000_000)
    factor = decimal_value(safety_factor, "estimate_safety_factor")
    total = (input_cost + output_text_cost + output_image_cost) * factor
    return {
        "input_text_tokens_upper_bound": text_tokens_upper_bound,
        "input_image_tokens_upper_bound": image_input_tokens_upper_bound,
        "output_tokens_upper_bound": output_tokens_upper_bound,
        "input_usd_upper_bound": cost_number(input_cost),
        "output_usd_upper_bound": cost_number(output_text_cost),
        "output_image_tokens_upper_bound": image_output_tokens_upper_bound,
        "output_image_usd_upper_bound": cost_number(output_image_cost),
        "safety_factor": float(factor),
        "estimated_cost_usd": cost_number(total),
        "model": model,
        "service_tier": service_tier,
        "billing_regime": pricing.get("billing_regime", "standard"),
        "price_source_url": pricing.get("source_url"),
        "price_verified_at": pricing.get("verified_at"),
    }


def calculate_usage_cost(usage: dict, pricing: dict, fallback_image_input_tokens: int = 0, fallback_image_output_tokens: int = 0) -> float:
    input_tokens = int(usage["input_tokens"])
    output_tokens = int(usage["output_tokens"])
    input_image_tokens = usage.get("input_image_tokens")
    output_image_tokens = usage.get("output_image_tokens")
    if input_image_tokens is None:
        input_image_tokens = fallback_image_input_tokens
        input_text_tokens = input_tokens
    else:
        input_image_tokens = min(input_tokens, max(0, int(input_image_tokens)))
        input_text_tokens = input_tokens - input_image_tokens
    if output_image_tokens is None:
        output_image_tokens = fallback_image_output_tokens
        output_text_tokens = output_tokens
    else:
        output_image_tokens = min(output_tokens, max(0, int(output_image_tokens)))
        output_text_tokens = output_tokens - output_image_tokens
    input_rate = decimal_value(pricing["input_usd_per_million"], "input price")
    image_input_rate = decimal_value(pricing.get("image_input_usd_per_million", pricing["input_usd_per_million"]), "image input price")
    output_rate = decimal_value(pricing["output_usd_per_million"], "output price")
    image_output_rate = decimal_value(pricing.get("image_output_usd_per_million", pricing["output_usd_per_million"]), "image output price")
    total = (
        Decimal(input_text_tokens) * input_rate
        + Decimal(input_image_tokens) * image_input_rate
        + Decimal(output_text_tokens) * output_rate
        + Decimal(output_image_tokens) * image_output_rate
    ) / Decimal(1_000_000)
    return cost_number(total)


def attempt_budget_cost(attempt: dict) -> Decimal:
    if attempt.get("consumption_status") == "reconciled_not_charged":
        return Decimal(0)
    reserve = decimal_value(attempt.get("reserved_cost_usd", attempt.get("estimated_cost_usd", 0)), "reservation")
    consumption = attempt.get("consumption_status")
    if consumption == "reconciled_charged":
        return decimal_value(attempt["reported_cost_usd"], "reconciled billing")
    if attempt.get("conservative_cost_usd") is not None:
        return max(reserve, decimal_value(attempt["conservative_cost_usd"]))
    if consumption in {"indeterminate", "indeterminate_until_response", "not_reported"} or attempt.get("status") == "in_flight":
        return reserve
    observed = []
    for key in ("cost_calculated_from_reported_usage_usd", "reported_cost_usd"):
        value = attempt.get(key)
        if value is not None:
            observed.append(decimal_value(value, key))
    if observed:
        # Reservation is a hold, not a second charge; the larger observed amount is
        # retained until billing reconciliation resolves the final amount.
        return max(observed)
    return reserve


def committed_budget_usd(state: dict) -> float:
    total = sum((attempt_budget_cost(attempt) for attempt in state.get("attempts", [])), Decimal(0))
    return cost_number(total)


def model_matches(config: dict, returned: str | None) -> bool:
    """Accept only the requested model or explicitly equivalent priced snapshots."""
    return returned == config["model"] or returned in config.get("model_capabilities", {}).get("equivalent_models", [])


def record_usage_cost(attempt: dict, usage: dict | None) -> None:
    if usage is None or attempt["consumption_status"] == "indeterminate":
        return
    pricing = attempt["pricing_snapshot"]
    missing = []
    conservative = dict(pricing)
    for side, prefix in (("input", "fallback_image_input_tokens"), ("output", "fallback_image_output_tokens")):
        detail = usage.get(f"{side}_image_tokens")
        if ((detail is None and attempt.get(prefix, 0))
                or (detail is not None and detail > usage[f"{side}_tokens"])):
            missing.append(side)
            rate = f"{side}_usd_per_million"
            conservative[rate] = max(decimal_value(pricing[rate]), decimal_value(pricing.get(f"image_{rate}", pricing[rate])))
    if missing:
        totals = {f"{side}_tokens": usage[f"{side}_tokens"] for side in ("input", "output")}
        for side in ("input", "output"):
            if side not in missing:
                totals[f"{side}_image_tokens"] = usage.get(f"{side}_image_tokens")
        attempt["conservative_cost_usd"] = calculate_usage_cost(totals, conservative)
        attempt["cost_assumptions"] = [f"All reported {side} tokens priced at the higher modality rate" for side in missing]
    else:
        attempt["cost_calculated_from_reported_usage_usd"] = calculate_usage_cost(usage, pricing)
