
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if current_question_id is None:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''

    if current_question_id is not None and 0 <= current_question_id < len(PYTHON_QUESTION_LIST):
        ques = PYTHON_QUESTION_LIST[current_question_id]
        options = ques["options"]
        correct_ans = ques["answer"]
        user_ans = session.get("user_answers", {})

        try:
            idx = int(answer.strip()) -1

            if 0 <= idx < len(options):
                user_ans[current_question_id] = {
                    "user_answer": options[idx],
                    "is_correct": options[idx] == correct_ans
                }
                session["user_answers"] = user_ans
                return True, ""
            else:
                return False, "Invalid option number. Please select a valid option (1, 2, 3, or 4)."
        except ValueError:
            return False, "Invalid input. Please enter the option number (1, 2, 3, or 4)."

    elif current_question_id is None:
        return True, ""
    return False, "Invalid question ID"


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''

    if current_question_id is None:
        next_question_id = 0
    else:
        next_question_id = current_question_id +1

    if next_question_id < len(PYTHON_QUESTION_LIST):
        next_question = PYTHON_QUESTION_LIST[next_question_id]["question_text"]
        options = PYTHON_QUESTION_LIST[next_question_id]["options"]
        formatted_options = "\n".join([f'{idx +1}. {option}' for idx, option in enumerate(options)])
        return f'{next_question}\n\n{formatted_options}', next_question_id
    return None, None


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''

    user_ans = session.get("user_answers", {})
    total_ques = len(PYTHON_QUESTION_LIST)
    correct_ans = sum(1 for ques_id in user_ans if user_ans[ques_id]["is_correct"])

    res = f'Quiz Completed! \nYour Score! {correct_ans}/{total_ques}\n'
    res += '\nBelow are your Answers:\n'

    for idx, ques in enumerate(PYTHON_QUESTION_LIST):
        ans = user_ans.get(idx, {}).get("user_answer", "No answer provided!")
        is_correct = user_ans.get(idx, {}).get("is_correct", False)
        status = 'Correct' if is_correct else "Incorrect"
        res += f'\nQ{idx +1}: {ques['question_text']}\n\nYour Answer: {ans}\nResult: {status}\n'

    session["current_question_id"] = None
    session["user_answers"] = {}
    session.save()

    return res
