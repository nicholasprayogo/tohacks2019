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
            this.tiebreakStep.bind(this),
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

    async ageStep(step) {
        // WaterfallStep always finishes with the end of the Waterfall or with another dialog; here it is a Prompt Dialog.
        // Running a prompt here means the next WaterfallStep will be run when the users response is received.
        return await step.prompt(CHOICE_PROMPT, {
            prompt: "Perfect, you came to the right person! I'm Finn and I can help you choose the bank account that suits you best. Let's get started. \n Which age group do you belong to?",
            choices: ChoiceFactory.toChoices(['19 and under', '20 and older'])
        });
    }

    async studentStep(step) {
        step.values.age = step.result.value;
        return await step.prompt(CHOICE_PROMPT, {
            prompt: 'Are you a full-time student?',
            choices: ChoiceFactory.toChoices(['Yes', 'No'])
        });
    }

    async etransferStep(step) {
        step.values.student = step.result.value;
        // WaterfallStep always finishes with the end of the Waterfall or with another dialog; here it is a Prompt Dialog.
        // Running a prompt here means the next WaterfallStep will be run when the users response is received.
        return await step.prompt(CHOICE_PROMPT, {
            prompt: 'How often do you think you\'d need to e-transfer money?',
            choices: ChoiceFactory.toChoices(['Never', 'Sometimes', 'Often'])
        });
    }

    async paymentStep(step) {
        step.values.etransfer = step.result.value;
        // WaterfallStep always finishes with the end of the Waterfall or with another dialog; here it is a Prompt Dialog.
        // Running a prompt here means the next WaterfallStep will be run when the users response is received.
        return await step.prompt(CHOICE_PROMPT, {
            prompt: 'How often do you see yourself buying stuff with this account?',
            choices: ChoiceFactory.toChoices(['Only when I need to', 'All the time'])
        });
    }

    async savingStep(step) {
        step.values.payment = step.result.value;
        // WaterfallStep always finishes with the end of the Waterfall or with another dialog; here it is a Prompt Dialog.
        // Running a prompt here means the next WaterfallStep will be run when the users response is received.
        return await step.prompt(CHOICE_PROMPT, {
            prompt: 'Do you need to save for anything right now?',
            choices: ChoiceFactory.toChoices(['Not really', 'It\'d be nice', 'Absolutely'])
        });
    }

	async tiebreakStep(step) {
        step.values.savings = step.result.value;
		return await step.prompt(CHOICE_PROMPT, {
			prompt: 'If you HAD to drop one, which would you pick?',
			choices: ChoiceFactory.toChoices(['Sending eTransfers', 'Making Purchases', 'Saving Money'])
		});
	}

    async summaryStep(step) {
        step.values.tiebreak = step.result.value;
        console.log("testing")
        if (step.result) {
            console.log("testing");
            // Get the current profile object from user state.
            const userProfile = await this.userProfile.get(step.context, new UserProfile());

            userProfile.age = step.values.age;
            userProfile.student = step.values.student;
            userProfile.etransfer = step.values.etransfer;
            userProfile.payment = step.values.payment;
            userProfile.savings = step.values.savings;
            userProfile.tiebreak = step.values.tiebreak;

			let selectLine = "SELECT * FROM Options c ";
			let general_query = "";
			let etransLine = "";
			let transLine = "";
			let savingsLine = "";
			let typeLine = "";
			let count = 0;

			// Student
			if(userProfile.student == "Yes") {
				typeLine = "WHERE c.type = @student ";
			}
			// Non-student; under 19
			else if(userProfile.age == "19 and under") {
				typeLine = "WHERE c.type = @youth ";
			}
			// Non-student; over 20
			else {
				typeLine = "WHERE c.type = @nonstudent ";
			}

			// Really wants etransfers
			if(userProfile.etransfer == "Often") {
				count++;
				etransLine = "AND c.etrans_num = @unlimited " ;
			}

			// Really wants to use card for transactions
			if(userProfile.payment == "All the time") {
				count++;
				transLine = "AND c.trans_num = @unlimited ";
			}

			// Really wants to save money
			if(userProfile.savings == "Absolutely") {
				count++;
				savingsLine = "AND c.savings != @none ";
			}

			// If there's a tie
			if(count == 3){

				if(userProfile.tiebreak == "Sending eTransfers") {
					general_query =  selectLine + typeLine + savingsLine + transLine;
				} else if(userProfile.tiebreak == "Saving Money") {
					general_query =  selectLine + typeLine + etransLine + transLine;
				} else {
					general_query =  selectLine + typeLine + etransLine + savingsLine;
				}
			}else {
        general_query =  selectLine + typeLine + transLine + etransLine + savingsLine;
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
				  {
                    name: "@none",
                    value: "0"
				  },
				]
            };

            //const msg  = await client.database(databaseId).container(containerId).items.query(querySpec);
            // const { result: results } = await container.items.query(querySpec).toArray();

            // await step.context.sendActivity(msg);
            //await console.log(msg);

			 const { result: results } = await client.database(databaseId).container(containerId).items.query(querySpec, {enableCrossPartitionQuery:true}).toArray();

       // for (var queryResult of results) {
				//  let resultString = JSON.stringify(queryResult);
       //   let account_name = resultString.name;
       //   let account_link = resultString.link;
				 // console.log(`\tQuery returned ${resultString}\n`);
			 // }

      console.log(results);
       if (results.length == 0 ){
           await step.context.sendActivity("No results. Try again");
       } else {
                let resultString = results[0] ;
                // console.log(queryResult);
                // let resultString = JSON.stringify(queryResult);
                // console.log(resultString);
                let account_name = resultString["name"];
                // console.log(account_name);
                let account_link = resultString["link"];
                // console.log(account_link);
                let transnum = resultString["trans_num"];
                let etransnum = resultString["etrans_num"];
                let transfee = resultString["trans_fee"];
                let etransfee = resultString["etrans_fee"];
                let interest = resultString["interest"];

                await step.context.sendActivity(`Your best option is ${account_name}`);

                let message = ``;

                // check trans
                if( transnum == "unlimited"){
                  message += `You get unlimited debit transactions, `;
                }else if (transnum != "0"){
                  message += `You pay ${transfee} per debit transaction after ${transnum} free transactions per month, `;
                }else {
                  message += `You pay ${transfee} per debit transaction, `;
                }

                // check etrans
               if( etransnum == "unlimited"){
                  message += `unlimited etransfers, `;
                }else if (transnum != "0"){
                  message += `pay ${etransfee} per etransfer after ${etransnum} free etransfers per month, `;
                }else {
                  message += `pay ${etransfee} per etransfer, `;
                }

                // check interest
                if( interest == "0"){
                   message += `with no interest on your average daily balance.`
                 }else{
                   message += `with ${interest} interest on your average daily balance.`
                 }

                 await step.context.sendActivity(`${message}`);
                 await step.context.sendActivity(`You can check it out here ${account_link}`);
               }

        } else {
            console.log("testing2")
            await step.context.sendActivity('Thanks.');
        }
        // WaterfallStep always finishes with the end of the Waterfall or with another dialog, here it is the end.
        return await step.endDialog();
    }

    // async agePromptValidator(promptContext) {
    //     // This condition is our validation rule. You can also change the value at this point.
    //     return promptContext.recognized.succeeded && promptContext.recognized.value > 0 && promptContext.recognized.value < 150;
    // }
}

module.exports.UserProfileDialog = UserProfileDialog;
