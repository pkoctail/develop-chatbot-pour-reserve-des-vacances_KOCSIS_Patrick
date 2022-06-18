# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Flight booking dialog."""

from datatypes_date_time.timex import Timex

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog


class BookingDialog(CancelAndHelpDialog):
    """Flight booking implementation."""

    def __init__(
        self,
        dialog_id: str = None,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(BookingDialog, self).__init__(
            dialog_id or BookingDialog.__name__, telemetry_client
        )
        self.telemetry_client = telemetry_client
        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = telemetry_client

        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__,
            [
                self.destination_step,
                self.origin_step,
                self.start_date_step,
                self.end_date_step,
                self.budget_step,
                self.confirm_step,
                self.final_step,
            ],
        )
        waterfall_dialog.telemetry_client = telemetry_client

        self.add_dialog(text_prompt)
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(waterfall_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__

    async def destination_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for destination."""
        booking_details = step_context.options

        if booking_details.dst_city is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Please tell me the destination you would like to travel to?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.dst_city )

    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for origin city."""
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.dst_city  = step_context.result
        if booking_details.or_city is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("From what city will you be travelling from?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.or_city)

    async def start_date_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for start travel date"""

        booking_details = step_context.options
        # Capture the results of the previous step
        booking_details.or_city = step_context.result
        if booking_details.str_date is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("What date would you like to depart?")
                ),
            )  # pylint: disable=line-too-long
        return await step_context.next(booking_details.str_date)

    async def end_date_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for end travel date"""
        booking_details = step_context.options
        # Capture the results of the previous step
        booking_details.str_date = step_context.result
        if booking_details.end_date is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("What date would you like to return ?")
                ),
            )  # pylint: disable=line-too-long
        return await step_context.next(booking_details.end_date)

    async def budget_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for end budget"""
        booking_details = step_context.options
        # Capture the results of the previous step
        booking_details.end_date = step_context.result
        if booking_details.budget is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("What budget will you use for this trip ?")
                ),
            )  # pylint: disable=line-too-long
        return await step_context.next(booking_details.budget)

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Confirm the information the user has provided."""
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.budget = step_context.result
        msg = (
            f"Please confirm, I have you traveling to: { booking_details.dst_city } on {booking_details.str_date}, "
            f" You are returning to: { booking_details.or_city }, on {booking_details.end_date}. "
            f"This trip will use your budget of {booking_details.budget} "
        )

        # Offer a YES/NO prompt. 
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=MessageFactory.text(msg))
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete the interaction and end the dialog."""
        booking_details = step_context.options
        properties = {}
        properties["dst_city"] = booking_details.dst_city
        properties["or_city"] = booking_details.or_city
        properties["str_date"] = booking_details.str_date
        properties["end_date"] = booking_details.end_date
        properties["budget"] = booking_details.budget

        severity_level = {0: "Verbose", 1: "Information", 2: "Warning", 3: "Error", 4: "Critical",}

        if step_context.result:
            self.telemetry_client.track_trace("YES answer", properties, severity_level[1])
            self.telemetry_client.flush()
            return await step_context.end_dialog(booking_details)
        else:
            sorry_msg = "I'm sorry we could not confirm your plans."
            prompt_sorry_msg = MessageFactory.text(sorry_msg, sorry_msg, InputHints.ignoring_input)
            await step_context.context.send_activity(prompt_sorry_msg)
            self.telemetry_client.track_trace("NO answer", properties, severity_level[3])
            self.telemetry_client.flush()
            
        return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
