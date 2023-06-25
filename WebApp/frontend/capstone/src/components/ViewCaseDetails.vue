<template>
  <div class="container">
    <v-container fluid>
      <v-row>
        <v-col cols="12" md="4">
          <h2>Case {{ caseDetails.id }} Details</h2>
          <div class="form-container">
            <!-- Case Details Form -->
            <v-row
              v-for="(value, key) in caseDetails"
              :key="key"
              class="d-flex align-center"
            >
            <template v-if="key !== 'raw_file_str' && 
              key !== 'cleaned_case_with_newlines' && 
              key != 'formatted_file_str' &&
              key !== 'full_file' &&
              key !== 'metadata' &&
              key !== 'content'">
              <v-col cols="12" class="field-description">{{ fieldDescriptions[key] }}</v-col>
              <v-col cols="12">
                <v-row align="center">
                  <v-spacer v-if="isSpanKey(key)"></v-spacer>
                  <template v-if="key !== 'approved'">
                    <v-text-field
                      :label="key"
                      v-model="caseDetails[key]"
                      :readonly="true"
                      :class="{'special-format': isSpanKey(key), 'disabled-field': true}"
                    ></v-text-field>
                  </template>
                  <template v-else>
                    <v-spacer></v-spacer>
                    <div :class="caseDetails[key] === '1' ? 'approved' : 'not-approved'">
                      Verified:
                      <v-icon :class="caseDetails[key] === '1' ? 'green-icon' : 'red-icon'">
                        {{ caseDetails[key] === '1' ? 'mdi-check' : 'mdi-close' }}
                      </v-icon>
                    </div>
                  </template>


                  <v-btn
                    v-if="isSpanKey(key)"
                    color="grey lighten-2"
                    @click="highlightSpan(key)"
                    style="margin-left: 10px;"
                  >
                    {{ buttonText[key] }}
                  </v-btn>
                </v-row>
              </v-col>
            </template>

            </v-row>
          </div>
        </v-col>
        <v-col cols="12" md="8">
          <h2>Case Content</h2>
          <div class="content-container">
            <v-card>
              <v-card-text @mouseup="highlightText">
                <pre v-html="caseDetails.formatted_file_str"></pre>
              </v-card-text>
            </v-card>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
      return {
          caseDetails: {},
          reviewed: {},
          highlightedKey: null,
          buttonText: {},
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
  async mounted() {
      const response = await axios.get(`http://localhost:8000/api/${this.id}`);
      this.caseDetails = response.data;

      for (let key in this.caseDetails) {
          if (key === "id") {
              this.reviewed[key] = true;
          } else {
              this.reviewed[key] = false;
          }
      }
      for (let key in this.caseDetails) {
        this.buttonText[key] = 'Show';
      }
  },
  methods: {
      isSpanKey(key) {
        return key.toLowerCase().includes('span');
      },
      highlightSpan(key) {
        let formatted_file_str = this.caseDetails.formatted_file_str;

        // Check if this is the same key as before
        if (this.highlightedKey === key) {
          // Clear the highlighting
          this.caseDetails.formatted_file_str = this.caseDetails.formatted_file_str.replace(/<mark>|<\/mark>/g, '');
          this.highlightedKey = null;
          this.buttonText[key] = 'Show'; // set button text to 'Show'
        } else {
          // Highlight the new span

          // First, clear any previous highlighting and set all buttons to 'Show'
          formatted_file_str = formatted_file_str.replace(/<mark>|<\/mark>/g, '');
          Object.keys(this.buttonText).forEach(k => this.buttonText[k] = 'Show');

          let spanString = this.caseDetails[key];
          let [start, end] = spanString.split(":").map(Number);

          let highlightedContent =
            formatted_file_str.substring(0, start) +
            "<mark>" +
            formatted_file_str.substring(start, end) +
            "</mark>" +
            formatted_file_str.substring(end);

          this.caseDetails.formatted_file_str = highlightedContent;
          this.highlightedKey = key;
          this.buttonText[key] = 'Hide'; // set button text to 'Hide'
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

.content-container {
  max-height: calc(100vh - 150px); /* Adjust the height as needed */
  overflow-y: auto;
}

.dialog-box {
  padding:10px;
}

.disabled-field input {
  opacity: 1 !important;
}
.highlighted {
  background-color: yellow;
}

.green-icon {
  color: green;
}

.red-icon {
  color: red;
}
.field-description {
    font-size: 1em;
    color: #666;
}

</style>
