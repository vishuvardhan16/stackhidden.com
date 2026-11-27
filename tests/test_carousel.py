"""Featured quote carousel behaviour and accessibility state.

Since Nov 6, 2026 each slide leads with the article: the publisher
masthead, the date, and the headline. The quote itself waits behind
"Read my quote", a native <details>. The owner asked for this because the
quote cards, with his name and title on every slide, were too much.
"""

from __future__ import annotations

import unittest

from helpers import BrowserTestCase


# Every quote, oldest first: its headline, and the quote word for word as
# published, spelling included ("favour", "prioritise"). The first six
# are the quotes the slides' screenshots and quote cards showed before
# Nov 6, 2026. The twenty-nine added Nov 20-21, 2026 were read off the
# live publisher pages, not the submitted-answer files: the published
# text can differ from what was submitted, and three of the seventeen
# file-sourced candidates did. The eleven added Nov 26, 2026, placements
# #36 to #46, were read off the live publisher pages the same way.
# The carousel shows them newest first since Nov 26, 2026 (SHOWN).
SLIDES = [
    (
        "EU AI Act: Training Data Requirements in 2026",
        "In practice, most teams have a labeling pipeline and a policy document, but no lineage. "
        "They can't tell you where a given training row came from, what transformations it went "
        "through, or whether the distribution that produced it has drifted since. A policy on "
        "paper and a safeguard inside the pipeline are not the same thing.",
    ),
    (
        "Golden Dataset: How to Build Trusted AI Evaluation Data",
        "A golden dataset is one whose lineage is auditable and whose behavior is continuously "
        "validated against the world it claims to represent. If you can't reconstruct how a "
        "dataset was built or detect when it stops matching production reality, the label "
        "accuracy is decoration.",
    ),
    (
        "How Data Teams Balance Access and Privacy",
        "Take one defect - a column renamed by an upstream team, or the loss of 20% of a day's "
        "events due to partial outages.",
    ),
    (
        "How Analytics Teams Turn Data Into Everyday Decisions",
        "A dashboard becomes part of regular decisions when it stops being a place people visit "
        "and starts showing up where the decision already happens.",
    ),
    (
        "How Software Leaders Make Room for Technical Debt",
        "Technical debt gets roadmap space on our team because we stopped asking for it as a "
        "favour and started planning it as a category.",
    ),
    (
        "How Software Product Teams Prioritize Customer Requests",
        "We prioritise the roadmap by asking what each item makes possible, and what waiting costs.",
    ),
    (
        "22 Ways to Justify Major IT Investments to Skeptical Executives",
        "IT investment cases fail when they are written in IT language: platforms, versions, architecture. "
        "They succeed when they are written as the business outcome the spending protects or creates.",
    ),
    (
        "How Software Teams Build Trust During Outages",
        "Silence is what customers fill with their worst guesses. A short message on schedule, saying what "
        "we know, what we do not know yet, and what we are doing next, reads as competence because it is "
        "verifiable.",
    ),
    (
        "How IT Leaders Build Trust in Business Data",
        "In my work, trust improves when every shared metric has one certified definition, calculated in "
        "one place, with its lineage visible.",
    ),
    (
        "How Data Leaders Communicate Uncertainty With Confidence",
        "It helps to state what the data cannot prove alongside the estimate itself, in the same view, so "
        "stakeholders act on the number with its limits in front of them.",
    ),
    (
        "How Engineering Teams Reduce Single-Person Knowledge Risk",
        "The risk is rarely that the one engineer leaves. It is that they go on holiday during the one "
        "incident their system produces all year.",
    ),
    (
        "How to Help High School Graduates with Limited Work Experience Answer Behavioral Interview Questions",
        "The mistake I correct first, with the early-career people I mentor, is the belief that behavioral "
        "questions require a job. They do not. They require evidence, and a high school graduate has more "
        "of it than they think.",
    ),
    (
        "How to Scale Managed Data Labeling for Computer Vision",
        "In annotation work, the bottleneck is validation at volume: labels keep arriving, but checking "
        "them takes longer than producing them, so errors found late mean rework across the whole dataset "
        "instead of a quarantined batch caught at intake.",
    ),
    (
        "How Engineering Teams Keep Technical Debt From Slowing Product Delivery",
        "Technical debt becomes urgent at a specific moment: when it starts charging interest on every "
        "unrelated change.",
    ),
    (
        "Turn Artificial Intelligence Pilots Into Lasting Business Value",
        "My test for a new initiative is simple. Name the weekly decision it changes, name the owner of "
        "the data it stands on, and name how you will know in ninety days whether it worked.",
    ),
    (
        "How Analytics Teams Turn Dashboards Into Daily Decisions",
        "We cut the front page down to the handful of numbers tied to decisions people made every week, "
        "and moved everything else a click away.",
    ),
    (
        "Cybersecurity Compliance: Essential Tools and Resources",
        "The resource I rely on most is not a vendor product. It is the practice of writing data validation "
        "and policy checks as code inside the pipeline, backed by a lineage record that shows where a field "
        "came from and which checks it passed.",
    ),
    (
        "The Biggest Concerns About Autonomous Vehicle Security",
        "The honest answer is that a hacked autonomous vehicle is not mainly a driving problem. It is a "
        "data problem.",
    ),
    (
        "Email Personalization for Every Customer: Tips and Examples",
        "Personalization that earns its keep is not using someone's name. It is proving you looked at their "
        "actual situation before you wrote.",
    ),
    (
        "Community Engagement In Smart Infrastructure: Best Practices & Success Stories",
        "When the community's fingerprints are on the definitions, later disagreements are about trade-offs "
        "everyone already understands.",
    ),
    (
        "Decoding Web3 Success: Insights from Industry Leaders",
        "A Web3 business that wants to last should publish how each headline figure was produced.",
    ),
    (
        "Blockchain for Good: Real-World Examples of Transparency in Charity",
        "Donors do not really have a transparency problem. They have a provenance problem.",
    ),
    (
        "How Software Teams Keep Customer Trust During Incidents",
        "Trust is protected by the corrections too. When our early understanding turns out wrong, we say so "
        "in the same channel, at the same prominence, without burying it in a longer update.",
    ),
    (
        "22 Unconventional Contract Clauses That Protected Businesses From Major Problems",
        "The clause I push for in platform and data tooling contracts is an evidence checkpoint with a clean "
        "exit: staged payments tied to the tool proving itself on our data at set intervals, and a no-penalty "
        "termination right if the evidence does not arrive.",
    ),
    (
        "How Business Leaders Protect High Performers From Burnout",
        "When a high performer starts showing signs of burnout, my first decision is to treat it as a "
        "workload design problem, not a resilience problem.",
    ),
    (
        "Prioritize Technology Modernization Before Risk Grows",
        "An aging system earns modernization when the cost of staying starts exceeding the cost of moving, "
        "and in my experience that crossover shows up in three places before it shows up in any strategy "
        "document.",
    ),
    (
        "How Data Teams Make Better Data Retention Decisions",
        "My rule is simple. Keep the trusted, well described output that teams actually query. Keep the raw "
        "input only long enough to reprocess it if a check fails or a source changes. After that, retention "
        "should be a decision, not a default.",
    ),
    (
        "How Engineering and Product Teams Resolve Customer Priority Conflicts",
        "Our principle is to split the request by trust, not by effort. We ask which part of the feature "
        "can be built on data we already validate and would defend to the customer today, and which part "
        "depends on data that still needs work.",
    ),
    (
        "Software Team Onboarding Practices That Help New Hires Contribute Sooner",
        "The change that made the biggest practical difference for us was treating onboarding as a "
        "documentation problem before treating it as a mentoring problem.",
    ),
    (
        "Data Leaders Share Ways to Build Lasting Adoption",
        "Teams will adopt a slower process that they trust. They will not keep using a faster one that "
        "leaves them guessing.",
    ),
    (
        "How IT Leaders Build Shared Priorities Across the Business",
        "Shared priorities do not come from a meeting where everyone lists what they want. They come from "
        "agreeing, in advance, on how competing requests will be judged.",
    ),
    (
        "How Software Leaders Reduce Technical Debt Without Stalling Delivery",
        "I rank technical debt by how often it touches customers. Debt in a part of the product that ships "
        "changes every week costs far more than debt in code nobody opens.",
    ),
    (
        "How Software Teams Reduce Risk From Critical Knowledge Gaps",
        "Reducing key person risk is not about spreading people thin. It is about making sure critical "
        "knowledge is shared through real work, clear notes on checks and failures, and gradual ownership.",
    ),
    (
        "Where Teams Let AI Act Without Asking",
        "The playbook had to be bounded, so it could only act inside its own scope. It had to pass an "
        "evaluation set written for that specific playbook.",
    ),
    (
        "25 Due Diligence Techniques for Evaluating Software Vendors Beyond Sales Presentations",
        "I never evaluate a data or AI tool on the vendor's demo data. My due diligence technique is to "
        "hand the vendor a test set we built ourselves: real-shaped data with known defects planted in it, "
        "duplicates, broken joins, values that drift out of range, records that should never pass "
        "validation.",
    ),
    (
        "How Software Teams Build Customer Trust During Outages",
        "I'm a software development engineer at Amazon Advertising, and I have been the person writing "
        "customer-facing updates during incidents on the insights platform my team runs. My rule for the "
        "first message is simple: say what is affected, say what we know, and say when the next update "
        "will come. I do not wait for the root cause, because customers are making decisions with or "
        "without us, and silence just hands the explanation to rumour.",
    ),
    (
        "How Customer Service Teams Rebuild Trust After Negative Feedback",
        "I start with what I can say is true, and I say it plainly. When a customer gives negative "
        "feedback after a disappointing experience, I name the specific change that caused it, its likely "
        "cause, and one concrete next step. I do not defend the old numbers and I do not promise a fix "
        "I cannot guarantee.",
    ),
    (
        "How IT Leaders Make Everyday Work More Secure",
        "The secure choice has to be the easy choice, or people will route around it under deadline "
        "pressure, and they will be right to. Where I work, the approach that holds up is to move "
        "security into the defaults of the systems people already use, instead of adding review steps "
        "they have to remember.",
    ),
    (
        "How Software Teams Build Better Engineering and Product Alignment",
        "The habit that made the biggest difference on my team is a short monthly review where every "
        "roadmap item has to restate its case in three lines: who it serves, what changes for them, and "
        "what it costs to delay by one quarter. Requests arrive as features. The honest unit is a "
        "decision or an outcome: a launch that cannot happen, a customer workflow that stays manual, a "
        "platform deadline that does not move.",
    ),
    (
        "How Analytics Teams Keep Work Focused on Business Value",
        "My test is simple: name the decision the initiative changes, and the date that decision gets "
        "made. If nobody can name both, the work is producing reports, not solving a problem.",
    ),
    (
        "How to Build Trust With Proactive Customer Communication",
        "I contact them right away if the problem affects a decision the customer is about to make. I "
        "only wait when the problem is still a suspicion and I have nothing concrete to tell them yet. "
        "The test is easy.",
    ),
    (
        "How Analytics Teams Catch Data Quality Problems Earlier",
        "I rank data quality issues by decision exposure: what decision is being made from this data, and "
        "when. An error in a feed behind a live advertiser report outranks a larger error in a dataset "
        "nobody has opened in a month. The second question is blast radius.",
    ),
    (
        "How IT Leaders Build Trust During Service Outages",
        "The practice that preserved trust in our incidents is a fixed update rhythm with honest content: "
        "what we know, what we do not know yet, and when the next update lands. Leaders can absorb bad "
        "news.",
    ),
    (
        "How Engineering Leaders Build Trust Through Better Feedback",
        "Feedback stops being a surprise when it attaches to the work while the work is still current. On "
        "my team that means the review cycle carries it: code reviews and design reviews where comments "
        "land on a specific decision, in writing, within days of the decision being made.",
    ),
    (
        "6 Nervous Habits and Communication Mistakes High School Graduates Should Eliminate Before Interviews: How to Address Them",
        "The habit I coach my mentees out of first is narrating their own nervousness. Opening with an "
        "apology for having no experience, or filling every pause with commentary about how nervous they "
        "are, spends the interviewer's attention on the apology instead of the evidence.",
    ),
    (
        "How Software Teams Keep Technical Debt From Stalling Progress",
        "We decide by cost of delay, stated out loud. A debt item earns attention now when it is blocking "
        "something with a date on it, a launch, a version deadline, a partner commitment, or when it is "
        "quietly taxing every change the team makes. Debt that is merely ugly, in a part of the system "
        "nobody is touching, we live with on purpose, and we say so, so living with it is a decision "
        "rather than drift.",
    ),
]
SHOWN = SLIDES[::-1]

SLIDE_STATE = """() => [...document.querySelectorAll('#quoteCarousel .slide')].map(s => {
    const link = s.querySelector('figcaption .slide-title a');
    const quote = s.querySelector('details.slide-quote blockquote');
    return {
        title: link ? link.textContent.trim() : null,
        href: link ? link.href : null,
        cite: quote ? quote.cite : null,
        quote: quote ? quote.textContent.trim() : null,
        open: !!s.querySelector('details.slide-quote[open]'),
        pictures: [...s.querySelectorAll('img')].filter(i => !i.classList.contains('pub-logo')).length,
        text: s.textContent
    };
})"""
ACTIVE = "[...document.querySelectorAll('#quoteCarousel .slide')].findIndex(s => s.classList.contains('on'))"
TRACK_HEIGHT = "Math.round(document.querySelector('#quoteCarousel .carousel-track').getBoundingClientRect().height)"


# The counter as a sighted visitor sees it: everything but the
# screen-reader words ("Quote", "of").
COUNT_SHOWN = """() => { const c = document.querySelector('#quoteCarousel .carousel-count');
    return [...c.childNodes].filter(n => !(n.classList && n.classList.contains('sr-only'))).map(n => n.textContent).join('').replace(/\\s+/g, ' ').trim(); }"""

class CarouselTest(BrowserTestCase):
    def test_the_counter_tracks_the_active_slide_and_next_advances(self) -> None:
        carousel = self.page.locator("#quoteCarousel")
        carousel.scroll_into_view_if_needed()

        slides = carousel.locator(".slide")

        # 46 slides since Nov 26, 2026: the six from Sep 30 to Nov 4,
        # then twenty-nine more, placements #7 to #35, and eleven more,
        # placements #36 to #46. The counter replaced 46 dots that day.
        self.assertEqual(46, slides.count())
        self.assertEqual("1 / 46", self.page.evaluate(COUNT_SHOWN))
        self.assertIn("on", slides.nth(0).get_attribute("class") or "")
        self.assertEqual("false", slides.nth(0).get_attribute("aria-hidden"))

        self.page.click("#quoteNext")

        self.assertEqual("2 / 46", self.page.evaluate(COUNT_SHOWN))
        self.assertIn("on", slides.nth(1).get_attribute("class") or "")
        self.assertNotIn("on", (slides.nth(0).get_attribute("class") or "").split())
        self.assertEqual("false", slides.nth(1).get_attribute("aria-hidden"))
        self.assertEqual("true", slides.nth(0).get_attribute("aria-hidden"))


class HeadlineFirstTest(BrowserTestCase):
    """Each slide leads with the article; its quote opens on request."""

    # Hold the slides still: these tests are about what a slide shows.
    reduced_motion = "reduce"

    def setUp(self) -> None:
        super().setUp()
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")
        self.page.evaluate("document.getElementById('quoteCarousel').scrollIntoView({block:'center'})")

    def summary_text(self) -> str:
        return self.page.inner_text("#quoteCarousel .slide.on summary").strip()

    def quote_visible(self) -> bool:
        return self.page.is_visible("#quoteCarousel .slide.on blockquote")

    def test_slides_lead_with_the_headline_and_no_picture_of_the_quote(self) -> None:
        slides = self.page.evaluate(SLIDE_STATE)
        self.assertEqual([title for title, _ in SHOWN], [s["title"] for s in slides])
        for s in slides:
            with self.subTest(title=s["title"]):
                # The headline links to the article the quote cites.
                self.assertTrue(s["href"].startswith("https://"))
                self.assertEqual(s["href"], s["cite"])
                # No screenshot or quote card: the only image is the logo.
                self.assertEqual(0, s["pictures"])
                # His name and title are not repeated on every slide.
                self.assertNotIn("Kaithapuram", s["text"])
                self.assertNotIn("Software Development Engineer", s["text"])
                # Every quote starts closed.
                self.assertFalse(s["open"])
        self.assertEqual("Read my quote", self.summary_text())
        self.assertFalse(self.quote_visible())

    def test_every_quote_is_word_for_word_as_published(self) -> None:
        quotes = [s["quote"] for s in self.page.evaluate(SLIDE_STATE)]
        self.assertEqual([quote for _, quote in SHOWN], quotes)

    def test_read_my_quote_opens_and_closes_the_quote(self) -> None:
        self.page.click("#quoteCarousel .slide.on summary")
        self.assertTrue(self.quote_visible())
        self.assertEqual("Hide quote", self.summary_text())
        self.assertEqual(SHOWN[0][1], self.page.inner_text("#quoteCarousel .slide.on blockquote").strip("“” \n"))
        self.page.click("#quoteCarousel .slide.on summary")
        self.assertFalse(self.quote_visible())
        self.assertEqual("Read my quote", self.summary_text())

    def test_the_keyboard_reaches_only_the_active_slide(self) -> None:
        # Off-stage slides are inert, so Tab goes from the active slide's
        # headline to its toggle and then to the arrows, never into a
        # slide that is not showing.
        self.assertEqual(
            [False] + [True] * 45,
            self.page.evaluate("[...document.querySelectorAll('#quoteCarousel .slide')].map(s => s.inert)"),
        )
        self.page.focus("#quoteCarousel .slide.on .slide-title a")
        self.page.keyboard.press("Tab")
        self.assertEqual("SUMMARY", self.page.evaluate("document.activeElement.tagName"))
        self.assertTrue(self.page.evaluate("document.activeElement.closest('.slide').classList.contains('on')"))
        self.page.keyboard.press("Enter")
        self.assertTrue(self.quote_visible())
        self.page.keyboard.press("Enter")
        self.assertFalse(self.quote_visible())
        self.page.keyboard.press("Tab")
        self.assertEqual("quotePrev", self.page.evaluate("document.activeElement.id"))

        # The next slide becomes the only reachable one.
        self.page.click("#quoteNext")
        self.assertEqual(
            [True, False] + [True] * 44,
            self.page.evaluate("[...document.querySelectorAll('#quoteCarousel .slide')].map(s => s.inert)"),
        )

    def test_moving_on_closes_the_quote_and_the_stage_settles(self) -> None:
        closed = self.page.evaluate(TRACK_HEIGHT)
        self.page.click("#quoteCarousel .slide.on summary")
        self.assertGreater(self.page.evaluate(TRACK_HEIGHT), closed)
        self.page.click("#quoteNext")
        self.assertEqual([False] * 46, [s["open"] for s in self.page.evaluate(SLIDE_STATE)])
        self.assertEqual(closed, self.page.evaluate(TRACK_HEIGHT))
        self.page.click("#quotePrev")
        self.assertEqual("Read my quote", self.summary_text())


class QuoteHoldsTheSlideTest(BrowserTestCase):
    """With motion on, an open quote stops the carousel moving on."""

    def test_an_open_quote_holds_its_slide(self) -> None:
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")
        self.page.evaluate("document.getElementById('quoteCarousel').scrollIntoView({block:'center'})")
        self.page.click("#quoteCarousel .slide.on summary")
        # Leave the carousel, so neither hover nor focus is what holds it.
        self.page.mouse.move(2, 2)
        self.page.evaluate("document.activeElement.blur()")
        self.page.wait_for_timeout(5600)
        self.assertEqual(0, self.page.evaluate(ACTIVE))
        self.assertTrue(self.page.is_visible("#quoteCarousel .slide.on blockquote"))
        # Closed again, the carousel moves on as before.
        self.page.evaluate("document.querySelector('#quoteCarousel .slide.on details').open = false")
        self.page.wait_for_function(f"({ACTIVE}) === 1", timeout=6500)


class PrintTest(BrowserTestCase):
    """A printed page carries every quote, and printing changes nothing."""

    reduced_motion = "reduce"

    def test_every_quote_prints_and_the_page_is_restored_after(self) -> None:
        # The visitor has the first quote open before printing.
        self.page.evaluate("document.querySelector('#quoteCarousel .slide.on details').open = true")
        self.page.emulate_media(media="print")
        self.page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        printed = self.page.evaluate(
            # checkVisibility(), not the box: the content of a closed
            # <details> keeps its layout box but is not rendered.
            # visibilityProperty too: slides waiting off stage are
            # visibility:hidden on screen, and print must undo that.
            """() => [...document.querySelectorAll('#quoteCarousel .slide')].map(s => ({
                quote: s.querySelector('blockquote').checkVisibility({ visibilityProperty: true }),
                toggle: getComputedStyle(s.querySelector('summary')).display
            }))"""
        )
        self.assertEqual([{"quote": True, "toggle": "none"}] * 46, printed)
        # One after another, not stacked in the carousel's shared cell.
        overlaps = self.page.evaluate(
            """() => { const r = [...document.querySelectorAll('#quoteCarousel .slide')].map(s => s.getBoundingClientRect());
                       return r.slice(1).filter((b, i) => b.top < r[i].bottom - 1).length; }"""
        )
        self.assertEqual(0, overlaps)
        self.page.evaluate("window.dispatchEvent(new Event('afterprint'))")
        self.page.emulate_media(media="screen")
        self.assertEqual(
            [True] + [False] * 45,
            [s["open"] for s in self.page.evaluate(SLIDE_STATE)],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
