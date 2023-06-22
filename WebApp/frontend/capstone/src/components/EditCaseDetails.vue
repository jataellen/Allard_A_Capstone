<template>
  <div class="container">
    <v-container fluid>
      <v-row>
        <v-col cols="12" md="4">
          <h2>Case {{ caseDetails.id }} Details</h2>
          <div class="form-container">
            <v-form ref="form" @submit.prevent="handleSubmit">
              <!-- Case Details Form -->
              <v-row>
                <v-col cols="2"><h5>Review</h5></v-col>
                <v-col cols="10"><h5>Field</h5></v-col>
              </v-row>
              <v-row
                v-for="(value, key) in editableCaseDetails"
                :key="key"
                class="d-flex align-center"
                dense
            >
                <v-col cols="12" class="field-description">{{ fieldDescriptions[key] }}</v-col>
                <v-col cols="2" v-if = !isApprovedKey(key)>
                    <v-checkbox
                        class="mr-2"
                        v-model="reviewed[key]"
                        :disabled="key === 'id'"
                        v-if="!isSpanKey(key)"
                    ></v-checkbox>
                </v-col>
                <v-col cols="10">
                    <v-row align="center">
                        <v-spacer v-if="isSpanKey(key)"></v-spacer>
                        <v-checkbox
                            :label="'Verified by human annotator'"
                            v-model="approvedAsBoolean"
                            v-if="key === 'approved'"
                        ></v-checkbox>

                        <v-text-field
                            :label="key"
                            v-model="editableCaseDetails[key]" 
                            :disabled="key === 'id'"
                            :class="{'special-format': isSpanKey(key)}"
                            @keyup.enter="$event.target.blur()"
                            v-else
                        ></v-text-field>
                        <v-btn
                            v-if="isSpanKey(key)"
                            color="grey lighten-2"
                            @click="setHighlight(key)"
                            style="margin-left: 10px;"
                        >
                            Set
                        </v-btn>
                    </v-row>
                    <v-spacer v-if="isSpanKey(key)" style="height: 20px;"></v-spacer>
                </v-col>
            </v-row>

              <v-row>
                <v-btn color="grey lighten-2" @click="checkAllCheckboxes">Check All Boxes</v-btn>
                <v-spacer></v-spacer>
                <v-btn :disabled="!allReviewed" class="custom-submit-button" type="submit">Submit</v-btn>
              </v-row>
              
              <!-- Dialog 1 -->
              <v-dialog v-model="dialog" persistent max-width="400">
                <v-card class="dialog-box">
                  <v-card-title class="headline">Confirmation</v-card-title>
                  <v-card-text class="dialog-text">Are you sure you want to update Case {{ caseDetails.id }}?</v-card-text>
                  <v-card-text class="dialog-text">This action cannot be undone.</v-card-text>
                  <v-card-actions class="dialog-actions">
                    <v-spacer></v-spacer>
                    <v-btn color="blue darken-1" text @click="dialog = false">Cancel</v-btn>
                    <v-btn color="blue darken-1" text @click="submitForm">Confirm</v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </v-form>
          </div>
        </v-col>
        <v-col cols="12" md="8">
          <h2>Case Content</h2>
          <div class="content-container">
            <v-card>
              <v-card-text @mouseup="highlightText" style="white-space: pre-wrap;" class="formatted-text">
                {{ caseDetails.formatted_file_str }}
              </v-card-text>
            </v-card>
          </div>
        </v-col>
      </v-row>
    </v-container>
    <!-- Dialog 2 -->
    <v-dialog v-model="confirmEditDialog" persistent max-width="400">
      <v-card class="dialog-box">
        <v-card-title class="headline">Confirmation</v-card-title>
        <v-card-text class="dialog-text">This page is already approved. Are you sure you want to edit it?</v-card-text>
        <v-card-actions class="dialog-actions">
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="goToHomePage">No, take me back</v-btn>
          <v-btn color="blue darken-1" text @click="proceedWithEdit">Yes, I'm sure</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
        return {
            dialog: false,
            caseDetails: {},
            editableCaseDetails: {}, // make editableCaseDetails part of the data
            reviewed: {},
            highlightedSpan: null,
            confirmEditDialog: false,
            fieldDescriptions: {
              'citation': 'Full Case Citation',
              'url': 'URL',
              'file_number': 'File Number',
              'language': 'Language',
              'year': 'Year',
              'ltb_location': 'What was the location of the landlord tenant board?',
              'hearing_date': 'What was the date of the hearing? [mm/dd/yyyy]',
              'decision_date': 'What was the date of the decision? [mm/dd/yyyy]',
              'adjudicating_member': 'Who was the member adjudicating the decision?',
              'outcome_text': 'What was the outcome of the case?',
              'landlord_represented': 'Did the decision state the landlord was represented?',
              'tenant_payment_plan': 'Did the tenant propose a payment plan?',
              'payment_plan_accepted': 'If the tenant did propose a payment plan, did the member accept the proposed payment plan?',
              'tenant_represented': 'Did the decision state the tenant was represented?',
              'tenant_arrears_payment_history': 'If the tenant had a history of arrears, did the decision mention a history of the tenant making payments on those arrears (separate from any payments made in response to the present eviction notice/hearing)?',
              'tenant_children': 'Did the decision state that the tenant had children living with them?',
              'tenant_employment': 'Was the tenant employed at the time of the hearing?',
              'tenant_gov_assistance': 'If the tenant was not employed, did the decision state the tenant was receiving any form of government assistance (e.g. OW, childcare benefits, ODSP, OSAP)?',
              'tenant_employment_stability': 'If the tenant was employed, did the decision state any doubts about the stability of employment e.g. lack of guaranteed hours, contract work, etc.?',
              'tenant_sufficient_income': 'Did the member find the tenant had sufficient income to pay rent?',
          },
        };
    },
    props: {
        id: {
            type: String,
            required: true
        }
    },
    computed: {
        // removing editableCaseDetails computed property
        allReviewed() {
            return Object.values(this.reviewed).every(val => val === true);
        },
        approvedAsBoolean: {
          get() {
            return this.editableCaseDetails.approved === '1';
          },
          set(newValue) {
            this.editableCaseDetails.approved = newValue ? '1' : '0';
          }
        },
    },
    async mounted() {
        const response = await axios.get(`http://localhost:8000/api/${this.id}`);
        this.caseDetails = response.data;

        // populate editableCaseDetails here
        this.editableCaseDetails = {...this.caseDetails};
        delete this.editableCaseDetails.metadata;
        delete this.editableCaseDetails.full_cleaned;
        delete this.editableCaseDetails.content;
        delete this.editableCaseDetails.raw_file_name;
        delete this.editableCaseDetails.raw_file_str;
        delete this.editableCaseDetails.cleaned_case_with_newlines;
        delete this.editableCaseDetails.full_file;
        delete this.editableCaseDetails.formatted_file_str;

        for (let key in this.editableCaseDetails) {
            if (key === "id") {
                this.reviewed[key] = true;
            } else {
                this.reviewed[key] = false;
            }
        }

        if (this.caseDetails.approved === "1") {
            this.confirmEditDialog = true;
        }
    },
    methods: {
        handleSubmit() {
            // Now, we only need to validate the form if all fields have been reviewed
            if (this.allReviewed) {
            this.dialog = true;
            }
        },
        async submitForm() {
            this.dialog = false;
            // this.$refs.form.validate(); // Add form validation

            // Prepare the data to be sent in the PUT request
            const data = { ...this.editableCaseDetails };

            try {
                // Make the PUT request to update the case details
                const response = await axios.put(`http://localhost:8000/api/${this.id}`, data);

                // Handle the response as needed
                this.caseDetails = { ...this.editableCaseDetails }; // update caseDetails with form inputs

                // Redirect to the home page
                this.$router.push('/');
            } catch (error) {
                // Handle the error
                console.error(error);
            }
        },
        highlightText() {
          let selection = window.getSelection();
          let selectedText = selection.toString();
          let startIndex = this.caseDetails.formatted_file_str.indexOf(selectedText);
          let endIndex = startIndex + selectedText.length;
          this.highlightedSpan = { start: startIndex, end: endIndex };
          console.log(this.highlightedSpan)
        },
        isSpanKey(key) {
          return key.toLowerCase().includes('span');
        },
        isApprovedKey(key) {
          return key==='approved';
        },
        setHighlight(key) {
            let spanString = `${this.highlightedSpan.start}:${this.highlightedSpan.end}`;
            this.editableCaseDetails[key] = spanString; // Change this line
            console.log(key, spanString)
        },
        proceedWithEdit() {
          this.confirmEditDialog = false;
          // Perform any additional actions needed to proceed with editing
        },
        goToHomePage() {
          this.confirmEditDialog = false;
          this.$router.push("/");
        },
        // Method to check all checkboxes
    checkAllCheckboxes() {
      for (let key in this.reviewed) {
        this.reviewed[key] = true;
      }
    },
    }
  };
  </script>
  
  <style scoped>
  .container {
    padding: 20px;
    display: flex;
    justify-content: center;
    align-items: flex-start;
  }
  
  .form-container {
    max-height: calc(100vh - 150px); /* Adjust the height as needed */
    overflow-y: auto;
    padding: 25px;
  }
  
.formatted-text {
  font-family: monospace;
}

  .content-container {
    max-height: calc(100vh - 150px); /* Adjust the height as needed */
    overflow-y: auto;
  }
  
  .left-section {
    background-color: pink;
    flex: 1;
    width: 33.33%; /* 1/3 of the width */
    padding-right: 20px;
  }
  
  .right-section {
    background-color: lightblue;
    flex: 2;
    width: 66.67%; /* 2/3 of the width */
  }
  
  .special-format {
    color: #0099cc;
  }

.custom-submit-button {
  background-color: #0099cc;
  color: #ffffff;
}
.field-description {
    font-size: 1em;
    color: #666;
}

.dialog-box {
  padding:10px;
}
  </style>
  