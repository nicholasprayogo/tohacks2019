// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

const {
    ChoiceFactory,
    ChoicePrompt,
    ComponentDialog,
    ConfirmPrompt,
    DialogSet,
    DialogTurnStatus,
    NumberPrompt,
    TextPrompt,
    WaterfallDialog
} = require('botbuilder-dialogs');
const { UserProfile } = require('../userProfile');

const CHOICE_PROMPT = 'CHOICE_PROMPT';
const CONFIRM_PROMPT = 'CONFIRM_PROMPT';
const NAME_PROMPT = 'NAME_PROMPT';
const NUMBER_PROMPT = 'NUMBER_PROMPT';
const USER_PROFILE = 'USER_PROFILE';
const WATERFALL_DIALOG = 'WATERFALL_DIALOG';

class UserProfileDialog extends ComponentDialog {
    constructor(userState, logger) {
        super('userProfileDialog');

        this.userProfile = userState.createProperty(USER_PROFILE);

        this.logger = logger;

        this.addDialog(new TextPrompt(NAME_PROMPT));
        this.addDialog(new ChoicePrompt(CHOICE_PROMPT));
        this.addDialog(new ConfirmPrompt(CONFIRM_PROMPT));
        this.addDialog(new NumberPrompt(NUMBER_PROMPT, this.agePromptValidator));

        this.addDialog(new WaterfallDialog(WATERFALL_DIALOG, [
            this.ageStep.bind(this),
            this.studentStep.bind(this),
            this.paymethodStep.bind(this),
            this.withdrawStep.bind(this),
            this.usedebitStep.bind(this),
        ]));

        this.initialDialogId = WATERFALL_DIALOG;
    }

    /**
     * The run method handles the incoming activity (in the form of a TurnContext) and passes it through the dialog system.
     * If no dialog is active, it will start the default dialog.
     * @param {*} turnContext
     * @param {*} accessor
     */
    async run(turnContext, accessor) {
        const dialogSet = new DialogSet(accessor);
        dialogSet.add(this);

        const dialogContext = await dialogSet.createContext(turnContext);
        const results = await dialogContext.continueDialog();
        if (results.status === DialogTurnStatus.empty) {
            await dialogContext.beginDialog(this.id);
        }
    }

    async ageStep(step) {
        // WaterfallStep always finishes with the end of the Waterfall or with another dialog; here it is a Prompt Dialog.
        // Running a prompt here means the next WaterfallStep will be run when the users response is received.
        return await step.prompt(CHOICE_PROMPT, {
            prompt: 'What is your age?',
            choices: ChoiceFactory.toChoices(['Under 19', '19-64', '65 & Over'])
        });
    }

    async studentStep(step) {
        step.values.age = step.result.value;
        return await step.prompt(CONFIRM_PROMPT, 'Are you a full-time student?', ['yes', 'no']);
    }

    async paymethodStep(step) {
        step.values.student = step.result.value;
        // WaterfallStep always finishes with the end of the Waterfall or with another dialog; here it is a Prompt Dialog.
        // Running a prompt here means the next WaterfallStep will be run when the users response is received.
        return await step.prompt(CHOICE_PROMPT, {
            prompt: 'How do you mostly pay for things?',
            choices: ChoiceFactory.toChoices(['Debit', 'Credit', 'Cash', 'Cheque'])
        });
    }

    async withdrawStep(step) {
        step.values.payment = step.result.value;
        // WaterfallStep always finishes with the end of the Waterfall or with another dialog; here it is a Prompt Dialog.
        // Running a prompt here means the next WaterfallStep will be run when the users response is received.
        return await step.prompt(CHOICE_PROMPT, {
            prompt: 'How many times a month do you withdraw money from the ATM?',
            choices: ChoiceFactory.toChoices(['<30', '>30'])
        });
    }

    async usedebitStep(step) {
        step.values.withdraw = step.result.value;
        // WaterfallStep always finishes with the end of the Waterfall or with another dialog; here it is a Prompt Dialog.
        // Running a prompt here means the next WaterfallStep will be run when the users response is received.
        return await step.prompt(CHOICE_PROMPT, {
            prompt: 'How many times a month do you use your debit card?',
            choices: ChoiceFactory.toChoices(['<30', '>30'])
        });
    }

    async summaryStep(step) {
        if (step.result) {
            // Get the current profile object from user state.
            const userProfile = await this.userProfile.get(step.context, new UserProfile());

            userProfile.age = step.values.age;
            userProfile.student = step.values.student;
            userProfile.paymentmethod = step.values.payment;
            userProfile.withdraw = step.values.withdraw;
            userProfile.usedebit = step.values.usedebit;
            let msg = `Your age is ${ userProfile.age }, your most used payment method is ${ userProfile.paymentmethod } .`;
            if (userProfile.age !== -1) {
                msg += ` And age as ${ userProfile.age }.`;
            }

            await step.context.sendActivity(msg);
        } else {
            await step.context.sendActivity('Thanks. Your profile will not be kept.');
        }

        // WaterfallStep always finishes with the end of the Waterfall or with another dialog, here it is the end.
        return await step.endDialog();
    }

    async agePromptValidator(promptContext) {
        // This condition is our validation rule. You can also change the value at this point.
        return promptContext.recognized.succeeded && promptContext.recognized.value > 0 && promptContext.recognized.value < 150;
    }
}

module.exports.UserProfileDialog = UserProfileDialog;
