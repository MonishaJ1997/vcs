from django.views import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json

from resumes.models import JobMatch, Resume
from resumes.utils import extract_resume_text, analyze_resume
@method_decorator(login_required, name='dispatch')
class ChatbotAskView(View):

    def post(self, request):

        # ---------------- REQUEST PARSE ----------------
        try:
            data = json.loads(request.body)
            question = data.get('question', '').strip().lower()
        except:
            return JsonResponse({'answer': 'Invalid request'}, status=400)

        if not question:
            return JsonResponse({'answer': 'Please type a question.'})

        user_type = "Pro" if is_pro_user(request.user) else "Free"
        response = ""

        greetings = ["hi", "hello", "hey", "hlo"]
        farewells = ["bye", "goodbye"]
        thanks = ["thanks", "thank you"]

        # ---------------- GREETINGS ----------------
        if any(word in question for word in greetings):
            response = "Hi 👋 How can I help your career today?"

        # ---------------- FAREWELL ----------------
        elif any(word in question for word in farewells):
            response = "Goodbye! Wishing you success 🚀"

        # ---------------- THANKS ----------------
        elif any(word in question for word in thanks):
            response = "You're welcome 😊"

        # ---------------- CODING FOLLOW UP (PRO) ----------------
        elif "coding" in question or "problem" in question:

            if user_type == "Free":
                response = "Upgrade to Pro to view coding interview problems."

            else:
                coding_questions = CompanyInterviewQuestion.objects.filter(
                    category__iexact="coding"
                )[:5]

                if coding_questions.exists():
                    result = "Coding Problems:\n"
                    for q in coding_questions:
                        diff = getattr(q, "difficulty", "Medium")
                        result += f"\n{q.question} (Difficulty: {diff})"
                    response = result
                else:
                    response = "No coding problems available."

        # ---------------- COMPANY INTERVIEW QUESTIONS (PRO) ----------------
        elif "interview" in question or "questions" in question:

            if user_type == "Free":
                response = "Company interview questions are available for Pro users only."

            else:
                company_match = re.search(r"(infosys|tcs|wipro|google|amazon)", question)

                if company_match:
                    company = company_match.group(1)

                    questions = CompanyInterviewQuestion.objects.filter(
                        company__icontains=company
                    )

                    if questions.exists():
                        result = f"{company.title()} Interview Questions:\n"
                        for q in questions:
                            result += f"\n[{q.category}] {q.question}"
                        response = result
                    else:
                        response = f"No interview questions found for {company.title()}."
                else:
                    response = "Please mention a company name."

        # ---------------- JOB MATCH % ----------------
        elif "match" in question:

            matches = JobMatch.objects.filter(
                user=request.user
            ).order_by('-percentage')[:3]

            if matches.exists():
                result = "Your Top Job Matches:\n"
                for m in matches:
                    result += f"{m.job.title} - {m.percentage}%\n"
                response = result
            else:
                response = "Upload your resume first to get job match results."

        # ---------------- RESUME ANALYSIS ----------------
        elif "analyze resume" in question or "skills" in question:

            resume = Resume.objects.filter(user=request.user).last()

            if resume:
                text = extract_resume_text(resume.resume_file.path)
                skills = analyze_resume(text)

                if skills:
                    response = f"Detected Skills: {', '.join(skills)}"
                else:
                    response = "No skills detected."
            else:
                response = "Please upload a resume first."

        # ---------------- RESUME HELP ----------------
        elif "resume" in question:
            if user_type == "Pro":
                response = "Upload your resume — I will analyze skills and give suggestions."
            else:
                response = "Upload resume. Upgrade to Pro for AI analysis."

        # ---------------- JOB HELP ----------------
        elif "job" in question:
            if user_type == "Pro":
                response = "I can show advanced AI job matches."
            else:
                response = "Browse jobs. Upgrade to Pro for AI matching."

        # ---------------- DEFAULT ----------------
        else:
            if user_type == "Pro":
                response = f"[Pro AI] Detailed answer for: '{question}'"
            else:
                response = f"[Free AI] Basic answer for: '{question}'"

        # ---------------- SAVE CHAT ----------------
        ChatConversation.objects.create(
            user=request.user,
            question=question,
            answer=response
        )

        return JsonResponse({'answer': response})







from django.views import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from resumes.models import Resume, JobMatch
from resumes.utils import extract_resume_text, analyze_resume, calculate_match
from jobs.models import Job
@method_decorator(login_required, name='dispatch')
class ChatbotUploadResumeView(View):
    def post(self, request):

        # Check user type
        if hasattr(request.user, 'profile') and getattr(request.user.profile, 'user_type', 'free') == 'pro':
            user_type = 'Pro'
        else:
            user_type = 'Free'

        # Free users cannot analyze resume
        if user_type == 'Free':
            return JsonResponse({'message': 'Resume analysis is only available for Pro users. Please upgrade.', 'user_type': user_type}, status=403)

        # Check if file uploaded
        if 'resume' not in request.FILES:
            return JsonResponse({'message': 'No file uploaded', 'user_type': user_type}, status=400)

        file = request.FILES['resume']

        # Save resume correctly
        resume = Resume.objects.create(
            user=request.user,
            resume_file=file,
            full_name=request.user.get_full_name(),
            email=request.user.email
        )

        # Extract text and analyze skills
        text = extract_resume_text(resume.resume_file.path)
        skills = analyze_resume(text)

        # Calculate job matches
        job_matches = []
        for job in Job.objects.all():
            percent = calculate_match(text, job.description)
            JobMatch.objects.create(user=request.user, job=job, percentage=percent)
            job_matches.append({'title': job.title, 'percent': percent})

        # Top 3 matches
        job_matches.sort(key=lambda x: x['percent'], reverse=True)
        top_matches = job_matches[:3]

        match_text = "\n".join([f"{j['title']} - {j['percent']}%" for j in top_matches])
        skills_text = ", ".join(skills) if skills else "No skills detected"

        # Return message + user type
        return JsonResponse({
            'message': f"✅ Resume analyzed!\nUser Type: {user_type}\nDetected Skills: {skills_text}\nTop Job Matches:\n{match_text}",
            'user_type': user_type
        })


from .permissions import is_pro_user
import re
from chatbot.models import CompanyInterviewQuestion, ChatConversation

