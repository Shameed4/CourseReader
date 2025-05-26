import pdfplumber
import pandas as pd
import re

def extract_courses_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        all_text = "\n".join(page.extract_text() for page in pdf.pages)
    
    course_pattern = r'^([A-Z]{3} \d{3}[A-Z]?)'
    courses = re.split(course_pattern, all_text, flags=re.MULTILINE)
    
    results = []
    for i in range(len(courses) - 1):
        if not re.match(course_pattern, courses[i]):
            continue
        sections = re.findall(
            r'(?:[A-Z]{2,}\s+)?'                # non-capturing prefix
            r'(?:\d{5}\s+)?'                    # ✅ non-capturing class number
            r'(\w+)\s+'                         # (1) Component
            r'([A-Z]?\d+)\s+'                   # (2) Section
            r'(APPT|HTBA|[MTWRFSU]+|RECR|RECT)\s+'        # (3) Days
            r'(\d{2}:\d{2}-\d{2}:\d{2}[AP]M|-|TBA)\s+'  # (4) Time
            r'(\d{2}-[A-Z]{3}-\d{4})\s+'        # (5) Start date
            r'(\d{2}-[A-Z]{3}-\d{4})\s+'        # (6) End date
            r'(TBA|[A-Za-z&/ ]+?)'              # (7) Building
            r'(TBA|\S*\d\w*)\s+'                # (8) Room
            r'(.+)$',                           # (9) Instructor
            courses[i+1],
            re.MULTILINE
        )
            
        for section in sections:
            section_type, section_no, days, times, _, _, building, room, instructor = section
            results.append({
                "Course Number": courses[i],
                "Section": f"{section_type} {section_no}",
                "Time": f"{days} {times}",
                "Location": f"{building}{room}",
                "Instructor": instructor
            })
            
    return pd.DataFrame(results)


if __name__ == "__main__":
    df = extract_courses_from_pdf("courses.pdf")
    print(df)
    df.to_csv("results.csv", index=False)