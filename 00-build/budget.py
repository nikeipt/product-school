"""Preflight budget for this text-only GPT-4o-mini lab, shared by drafter and critic.

Rates verified 2026-09-15: https://developers.openai.com/api/docs/models/gpt-4o-mini
A deliberately conservative reservation may stop a run before its actual spend
reaches the cap. This is per process/run, not an account-wide billing limit.
"""
import json
from decimal import Decimal
from types import SimpleNamespace


class BudgetExceeded(RuntimeError):
    pass


class BudgetClient:
    # Reserve the entire model context window conservatively.
    # A 64KB text payload plus generous framing allowance fits this reservation.
    MAX_PAYLOAD_BYTES = 64_000
    INPUT_RESERVE = 128_000
    OUTPUT_LIMIT = 16_384
    INPUT_RATE = Decimal('0.15')
    OUTPUT_RATE = Decimal('0.60')

    def __init__(self, client, *, cap, model):
        self.cap = Decimal(str(cap))
        if not self.cap.is_finite() or not 0 < self.cap <= Decimal('0.50'):
            raise ValueError('Cortex requires a positive per-run cap of at most $0.50.')
        if model != 'gpt-4o-mini':
            raise ValueError('This budget is configured for gpt-4o-mini only.')
        self.client, self.model = client, model
        self.spent = Decimal('0')
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        if kwargs.get('model') != self.model:
            raise BudgetExceeded('Unpriced model blocked.')
        def encode(value):
            return value.model_dump(exclude_none=True)
        payload = json.dumps(kwargs, default=encode, ensure_ascii=True)
        if len(payload.encode('utf-8')) > self.MAX_PAYLOAD_BYTES:
            raise BudgetExceeded('Request exceeds the conservative 64KB budget envelope.')
        reserve = (self.INPUT_RESERVE * self.INPUT_RATE +
                   self.OUTPUT_LIMIT * self.OUTPUT_RATE) / Decimal(1_000_000)
        if self.spent + reserve > self.cap:
            raise BudgetExceeded(f'${self.cap} per-run cap: insufficient budget for next call.')
        # Reserve BEFORE sending. On failure/unknown usage keep the full reservation.
        self.spent += reserve
        try:
            response = self.client.chat.completions.create(
                **kwargs,
                max_completion_tokens=self.OUTPUT_LIMIT, service_tier='default')
        except Exception as exc:
            raise BudgetExceeded('API call failed; full reservation retained and run stopped.') from exc
        usage = response.usage
        if usage is None:
            raise BudgetExceeded('Missing usage; full reservation retained and run stopped.')
        if not (0 <= usage.prompt_tokens <= self.INPUT_RESERVE and
                0 <= usage.completion_tokens <= self.OUTPUT_LIMIT):
            raise BudgetExceeded('Usage outside budget envelope; run stopped.')
        cost = (usage.prompt_tokens * self.INPUT_RATE +
                usage.completion_tokens * self.OUTPUT_RATE) / Decimal(1_000_000)
        self.spent -= reserve - cost
        return response
