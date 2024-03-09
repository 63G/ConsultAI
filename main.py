import os
from openai import OpenAI


class Chatbot:
    def __init__(self, case_study):
        self.case_study = case_study
        # Ensure your OPENAI_API_KEY environment variable is set,
        # or set it here directly (though not recommended for security reasons).
        self.client = OpenAI(api_key=os.getenv("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"))

    def generate_prompt(self, user_question):
        """
        Creates a prompt for GPT-3 that includes the case study details and the user's question.
        """
        prompt = f"Case Study: {self.case_study.title}\n"
        prompt += f"Details: {self.case_study.details}\n\n"
        prompt += "Following are questions and answers based on the case study:\n"
        for question, info in self.case_study.questions.items():
            prompt += f"- Q: What is {question}?\n- A: {info}\n"
        prompt += f"\nQ: {user_question}\nA:"
        return prompt

    def ask_question(self, user_question):
        """
        Sends the user's question to GPT-3 and returns the generated response.
        """
        messages = [{"role": "user", "content": self.generate_prompt(user_question)}]

        try:
            chat_completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return chat_completion.choices[0].message['content']
        except Exception as e:
            print(f"An error occurred: {e}")
            return "I'm sorry, I couldn't process that question."


class CaseStudy:
    def __init__(self, title, details, questions):
        """
        Initializes a new instance of the CaseStudy class.

        :param title: A string representing the title of the case study.
        :param details: A string providing a detailed description of the case study.
        :param questions: A dictionary where keys are question topics or keywords,
                          and values are information related to those topics, intended
                          to guide the student without directly providing the solution.
        """
        self.title = title
        self.details = details
        self.questions = questions






def main():
    # Example usage:
    case_study_info = CaseStudy(
        title="Renewable Energy Project",
        details="This case study focuses on the development of a renewable energy project in a rural area...",
        questions={
            "planning": "The planning phase involves assessing the energy needs...",
            "implementation": "Implementation includes the installation of solar panels and wind turbines...",
        }
    )

    chatbot = Chatbot(case_study_info)
    question = input("Ask away!\n Enter your question here:")
    response = chatbot.ask_question(question)
    print(response)


if __name__ == "__main__":
    main()

