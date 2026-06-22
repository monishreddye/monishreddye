import unittest

from hireitpeople_resume_scraper import parse_resume, resume_to_markdown


SAMPLE_HTML = """
<!doctype html>
<html>
  <head>
    <title>Senior Java Developer Resume New York, NY - Hire IT People - We get IT done</title>
  </head>
  <body>
    <section class="view-resume-page">
      <h3>Senior Java Developer Resume </h3>
      <span><b>4.20</b><small>/5</small></span>
      <h4 class="text-greish"><i class="fa fa-map-marker"></i>New York, NY</h4>
      <div class="single-post-body">
        <p>
          <p><strong>Objective:</strong></p>
          <p>Senior Java/J2EE Application developer.</p>
          <p><u><strong>Summary</strong></u><strong>:</strong></p>
          <p><strong>10.5 years of experience</strong> in architecture and development.</p>
          <p><u><strong>Specialties</strong></u>:</p>
          <ul>
            <li>Expert in core Java development.</li>
            <li>Experienced in multithreaded Java applications.</li>
          </ul>
          <p><strong>Skills:</strong></p>
          <p><strong>Technology:</strong> Java, J2EE, JDBC</p>
          <p><strong>Database</strong>: DB2, Oracle</p>
          <p><u><strong>Work Experience Summary:</strong></u></p>
          <p>Confidential / Confidential</p>
          <p>Senior Java Developer</p>
          <p><strong>Project Description:</strong> Real time trading application.</p>
          <p><strong>Responsibilities:</strong></p>
          <ul>
            <li>Gathered new requirements.</li>
            <li>Supported the application.</li>
          </ul>
          <p><strong>Environment</strong>: Java, Spring, Hibernate.</p>
          <p>Confidential</p>
          <p>Java Developer</p>
          <p><strong>Project Description:</strong> Debt services extension.</p>
          <p><strong>Responsibility:</strong></p>
          <p>Designed, developed and unit tested screens.</p>
          <p><strong>Environment</strong>: Java, Struts, Oracle.</p>
        </p>
      </div>
    </section>
  </body>
</html>
"""


class HireItPeopleResumeScraperTest(unittest.TestCase):
    def test_parse_resume_restructures_resume_body(self) -> None:
        resume = parse_resume(SAMPLE_HTML, "https://example.test/resume")

        self.assertNotIn("title", resume)
        self.assertNotIn("rating", resume)
        self.assertNotIn("source_url", resume)
        self.assertNotIn("raw_text", resume)
        self.assertEqual(resume["location"], "New York, NY")
        self.assertEqual(resume["objective"], "Senior Java/J2EE Application developer.")
        self.assertEqual(
            resume["summary"],
            "10.5 years of experience in architecture and development.",
        )
        self.assertEqual(
            resume["specialties"],
            ["Expert in core Java development.", "Experienced in multithreaded Java applications."],
        )
        self.assertEqual(resume["skills"]["Technology"], ["Java", "J2EE", "JDBC"])
        self.assertEqual(resume["skills"]["Database"], ["DB2", "Oracle"])

        self.assertEqual(len(resume["work_experience"]), 2)
        first_job = resume["work_experience"][0]
        self.assertEqual(first_job["company"], "Confidential / Confidential")
        self.assertEqual(first_job["title"], "Senior Java Developer")
        self.assertEqual(first_job["project_description"], "Real time trading application.")
        self.assertEqual(
            first_job["responsibilities"],
            ["Gathered new requirements.", "Supported the application."],
        )
        self.assertEqual(first_job["environment"], ["Java", "Spring", "Hibernate."])

        second_job = resume["work_experience"][1]
        self.assertEqual(second_job["company"], "Confidential")
        self.assertEqual(second_job["responsibilities"], ["Designed, developed and unit tested screens."])
        self.assertNotIn("notes", second_job)

    def test_parse_resume_can_include_metadata_when_requested(self) -> None:
        resume = parse_resume(
            SAMPLE_HTML,
            "https://example.test/resume",
            include_metadata=True,
            include_raw=True,
        )

        self.assertEqual(resume["location"], "New York, NY")
        self.assertEqual(resume["metadata"]["title"], "Senior Java Developer Resume")
        self.assertEqual(resume["metadata"]["rating"], {"score": 4.2, "scale": 5.0})
        self.assertEqual(resume["metadata"]["source_url"], "https://example.test/resume")
        self.assertIn("Objective:", resume["raw_text"])

    def test_markdown_output_contains_restructured_sections(self) -> None:
        resume = parse_resume(SAMPLE_HTML, "https://example.test/resume")
        markdown = resume_to_markdown(resume)

        self.assertNotIn("Senior Java Developer Resume", markdown)
        self.assertNotIn("4.2/5", markdown)
        self.assertIn("**Location:** New York, NY", markdown)
        self.assertIn("## Skills", markdown)
        self.assertIn("### Senior Java Developer", markdown)
        self.assertIn("- Gathered new requirements.", markdown)


if __name__ == "__main__":
    unittest.main()
