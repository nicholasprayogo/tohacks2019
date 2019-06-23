// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.
const CosmosClient = require('@azure/cosmos').CosmosClient;
const config = require('../config');

// const endpoint = config.endpoint;
// const masterKey = config.primaryKey;

const endpoint = "https://tohacks-sql.documents.azure.com:443/";
const masterKey = "rVffuZftq16dKAIkAfsh81tdgo2UUjogYtpeSv0WtWGWWogovgjLKtlHBhkq1OKoLkmc5FV9UbpxfLv1hVhVUg==";
const databaseId = "TOHacks Data"
const containerId = "Options"
const client = new CosmosClient({ endpoint: endpoint, auth: { masterKey: masterKey } });

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
            //this.introStep.bind(this),
            this.ageStep.bind(this),
            this.studentStep.bind(this),
            this.etransferStep.bind(this),
            this.paymentStep.bind(this),
            this.savingStep.bind(this),
            this.summaryStep.bind(this)
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

    // introStep(step) {
    //     return step.context.sendActivity('Hi. I am Finn.');
    //   }
    // async introStep(step){
    //     await wait(500);
    //     return step.context.sendActivity('Hi. I am Finn.');
    // }

    async ageStep(step) {
        // WaterfallStep always finishes with the end of the Waterfall or with another dialog; here it is a Prompt Dialog.
        // Running a prompt here means the next WaterfallStep will be run when the users response is received.
        return await step.prompt(CHOICE_PROMPT, {
            prompt: 'Which age group do you belong to?',
            choices: ChoiceFactory.toChoices(['19 and under', '20 and older'])
        });
    }

    // async studentStep(step) {
    //     step.values.age = step.result.value;
    //     return await step.prompt(CONFIRM_PROMPT, 'Are you a full-time student?', ['yes', 'no']);
    // }

    async studentStep(step) {
        step.values.age = step.result.value;
        return await step.prompt(CHOICE_PROMPT, {
            prompt: 'Are you a full-time student',
            choices: ChoiceFactory.toChoices(['Yes', 'No'])
        });
    }

    async etransferStep(step) {
        step.values.student = step.result.value;
        // WaterfallStep always finishes with the end of the Waterfall or with another dialog; here it is a Prompt Dialog.
        // Running a prompt here means the next WaterfallStep will be run when the users response is received.
        return await step.prompt(CHOICE_PROMPT, {
            prompt: 'How often would you want to e-transfer',
            choices: ChoiceFactory.toChoices(['Never', 'Sometimes', 'Often'])
        });
    }

    async paymentStep(step) {
        step.values.etransfer = step.result.value;
        // WaterfallStep always finishes with the end of the Waterfall or with another dialog; here it is a Prompt Dialog.
        // Running a prompt here means the next WaterfallStep will be run when the users response is received.
        return await step.prompt(CHOICE_PROMPT, {
            prompt: 'How often would you use your card to pay for things?',
            choices: ChoiceFactory.toChoices(['Never', 'Sometimes', 'Often'])
        });
    }

    async savingStep(step) {
        step.values.payment = step.result.value;
        // WaterfallStep always finishes with the end of the Waterfall or with another dialog; here it is a Prompt Dialog.
        // Running a prompt here means the next WaterfallStep will be run when the users response is received.
        return await step.prompt(CHOICE_PROMPT, {
            prompt: 'How important is saving to you?',
            choices: ChoiceFactory.toChoices(['1', '2', '3', '4', '5'])
        });
    }

    async summaryStep(step) {
        console.log("testing")
        if (step.result) {
            console.log("testing");
            // Get the current profile object from user state.
            const userProfile = await this.userProfile.get(step.context, new UserProfile());

            userProfile.age = step.values.age;
            userProfile.student = step.values.student;
            userProfile.etransfer = step.values.etransfer;
            userProfile.payment = step.values.payment;
            userProfile.saving = step.values.saving;
            // const { body: databaseDefinition } = await client.database(databaseId).read();
            // let msg = `Your age is ${ userProfile.age }, your most used payment method is ${ userProfile.paymentmethod } .`;

			let general_query = "SELECT * FROM Options c ";

			if(userProfile.student == "Yes") {
				general_query += "WHERE c.type = @student ";
				if(userProfile.etransfer == "Often") {
					general_query += "AND c.etrans_num = @unlimited " ;
					if(userProfile.payment == "Often") {
						general_query += "AND c.trans_num = @unlimited";
					}
				}
			}
			
			console.log(general_query);


            const querySpec = {
               //query: "SELECT * FROM Options c WHERE c.type = @type",
               query: general_query,
			    parameters: [
                  {
                    name: "@student",
                    value: "student"
                  },
				  {
                    name: "@unlimited",
                    value: "unlimited"
				  },
				]
            };

            //const msg  = await client.database(databaseId).container(containerId).items.query(querySpec);
            // const { result: results } = await container.items.query(querySpec).toArray();

            // await step.context.sendActivity(msg);
            //await console.log(msg);

			 const { result: results } = await client.database(databaseId).container(containerId).items.query(querySpec, {enableCrossPartitionQuery:true}).toArray();
			 for (var queryResult of results) {
				 let resultString = JSON.stringify(queryResult);
				 console.log(`\tQuery returned ${resultString}\n`);
			 }

        } else {
            console.log("testing2")
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
