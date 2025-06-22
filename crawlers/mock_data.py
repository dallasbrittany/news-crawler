from typing import List, Optional
from datetime import datetime, timedelta
from fundus import Article


def normalize_source_name(name: str) -> str:
    """Normalize source name by removing spaces and special characters."""
    return "".join(name.split())


MOCK_ARTICLES = [
    {
        "title": "Climate Change: A Global Challenge",
        "url": "https://example.com/climate-change",
        "body": "Climate change continues to be a pressing issue. Scientists warn about rising temperatures and their impact on ecosystems. Recent studies show concerning trends in global warming.",
        "source": "The Guardian",
        "publishing_date": datetime.now() - timedelta(days=1),
        "authors": ["Emma Thompson", "James Wilson"],
    },
    {
        "title": "Tech Giants Face New Regulations",
        "url": "https://example.com/tech-regulations",
        "body": "Major technology companies are facing increased scrutiny over data privacy and market dominance. Lawmakers propose new regulations to address concerns.",
        "source": "The New Yorker",
        "publishing_date": datetime.now() - timedelta(days=2),
        "authors": ["Sarah Chen"],
    },
    {
        "title": "Advances in AI Technology",
        "url": "https://example.com/ai-advances",
        "body": """Artificial intelligence continues to evolve with new breakthroughs in machine learning and neural networks. Researchers develop more efficient algorithms that are transforming industries across the globe.

In the field of natural language processing, large language models have achieved unprecedented capabilities in understanding and generating human-like text. These models are now being used in customer service, content creation, and even scientific research. The latest models can process and analyze vast amounts of data, identifying patterns that were previously impossible to detect.

Computer vision has also seen remarkable progress, with AI systems now able to identify objects, people, and even emotions with near-human accuracy. This technology is being applied in autonomous vehicles, medical imaging, and security systems. The integration of AI with edge computing has enabled real-time processing of visual data, opening up new possibilities for smart cities and industrial automation.

In healthcare, AI is revolutionizing diagnostics and treatment planning. Machine learning algorithms can analyze medical images to detect diseases earlier and with greater accuracy than traditional methods. AI-powered systems are also helping to predict patient outcomes and optimize treatment plans, leading to more personalized and effective healthcare.

The development of quantum computing is expected to further accelerate AI capabilities. Quantum algorithms could potentially solve complex optimization problems that are currently intractable for classical computers. This could lead to breakthroughs in drug discovery, materials science, and climate modeling.

However, these advances also raise important ethical considerations. The increasing power of AI systems necessitates careful consideration of privacy, bias, and accountability. Researchers and policymakers are working to establish frameworks that ensure AI development proceeds in a responsible and beneficial manner.

The future of AI looks promising, with ongoing research in areas like explainable AI, which aims to make AI decision-making processes more transparent and understandable. As these technologies continue to evolve, they will likely transform our society in ways we are only beginning to imagine.""",
        "source": "Wired",
        "publishing_date": datetime.now() - timedelta(days=3),
        "authors": ["Michael Rodriguez", "David Kim", "Lisa Patel"],
    },
    {
        "title": "Healthcare Innovation During Pandemic",
        "url": "https://example.com/healthcare-innovation",
        "body": """The healthcare sector has seen rapid innovation in response to global challenges. Telemedicine and digital health solutions have become mainstream, fundamentally transforming how medical care is delivered and accessed worldwide.

The pandemic accelerated the adoption of telemedicine by decades, forcing healthcare systems to rapidly implement remote consultation platforms. What was once considered a niche service became essential infrastructure overnight. Hospitals and clinics that had never offered virtual care suddenly found themselves conducting the majority of their consultations through video calls. This shift not only maintained continuity of care during lockdowns but also revealed the potential for more accessible and efficient healthcare delivery.

Digital health platforms experienced unprecedented growth during this period. Mobile health applications saw user engagement increase by over 300%, with patients actively monitoring symptoms, medication adherence, and vital signs from their homes. Wearable devices became crucial tools for early detection of health issues, with some smartwatches capable of detecting irregular heart rhythms and even early signs of respiratory infections.

Artificial intelligence played a pivotal role in pandemic response efforts. Machine learning algorithms were deployed to analyze chest X-rays and CT scans, helping radiologists identify COVID-19 pneumonia patterns with remarkable accuracy. AI-powered diagnostic tools reduced the time needed for preliminary diagnosis from hours to minutes, enabling faster treatment decisions and better resource allocation in overwhelmed hospitals.

The development of mRNA vaccines represented one of the most significant scientific achievements in recent history. The speed at which these vaccines were developed, tested, and deployed showcased the power of modern biotechnology and international collaboration. The success of mRNA technology has opened new possibilities for treating other diseases, including cancer and genetic disorders, with researchers now exploring personalized vaccine approaches.

Remote patient monitoring systems became essential for managing chronic conditions and post-acute care. Patients recovering from COVID-19 or other illnesses could be monitored from home using connected devices that tracked oxygen levels, heart rate, and other vital signs. This approach reduced hospital readmissions while allowing patients to recover in the comfort of their own homes, improving both outcomes and patient satisfaction.

Mental health services underwent a digital transformation as well. Teletherapy platforms saw explosive growth as people struggled with isolation, anxiety, and depression during lockdowns. Digital mental health tools, including AI-powered chatbots and meditation apps, provided accessible support for millions of people who might not have otherwise sought help. This shift helped reduce the stigma around mental health care and made services more widely available.

Healthcare supply chain management was revolutionized through the use of blockchain technology and IoT sensors. These innovations provided real-time visibility into the availability and location of critical supplies, from personal protective equipment to vaccines. Smart inventory systems helped prevent shortages and ensured that resources were distributed where they were needed most.

The integration of electronic health records (EHRs) with public health surveillance systems enabled more effective contact tracing and outbreak monitoring. Real-time data sharing between healthcare providers and public health authorities facilitated faster response times and more targeted interventions. This integration also supported research efforts by providing researchers with anonymized data to study disease patterns and treatment effectiveness.

Robotic systems found new applications in healthcare settings, from disinfection robots that could sanitize hospital rooms to delivery robots that reduced human contact while transporting supplies and medications. Surgical robots enabled some procedures to continue even when healthcare workers were in quarantine, ensuring that critical care could be maintained.

The future of healthcare has been permanently altered by these innovations. Hybrid care models that combine in-person and virtual consultations are becoming the new standard. Patients now expect the convenience and accessibility of digital health services, while healthcare providers have recognized the efficiency and cost-effectiveness of these technologies.

Investment in healthcare technology reached record levels, with venture capital funding for digital health startups exceeding previous years by significant margins. This influx of capital is driving continued innovation in areas such as precision medicine, personalized therapeutics, and predictive analytics.

As we move forward, the lessons learned during the pandemic continue to shape healthcare innovation. The emphasis on preparedness, resilience, and adaptability has become central to healthcare planning. The successful integration of technology into healthcare delivery has demonstrated that the sector can evolve rapidly when faced with urgent challenges, setting the stage for continued transformation in the years to come.""",
        "source": "The Guardian",
        "publishing_date": datetime.now() - timedelta(days=4),
        "authors": ["Dr. Rachel Foster"],
    },
    {
        "title": "Sustainable Energy Solutions",
        "url": "https://example.com/sustainable-energy",
        "body": """Renewable energy adoption continues to grow worldwide. Solar and wind power installations reach record levels as costs decrease, making clean energy more accessible than ever before.

Solar energy has seen particularly dramatic growth, with photovoltaic technology becoming increasingly efficient and affordable. New developments in perovskite solar cells promise even higher efficiency rates, potentially revolutionizing the solar industry. Large-scale solar farms are being constructed in previously untapped regions, while residential solar installations are becoming commonplace in urban areas.

Wind energy is also experiencing significant advancements. Offshore wind farms are being developed in deeper waters, taking advantage of stronger and more consistent winds. New turbine designs are increasing energy output while reducing environmental impact. Floating wind turbines are opening up new possibilities for energy generation in deep ocean waters.

Energy storage solutions are critical to the success of renewable energy. Breakthroughs in battery technology, including solid-state batteries and flow batteries, are improving energy density and reducing costs. Grid-scale storage systems are being deployed to manage the intermittent nature of renewable energy sources, ensuring reliable power supply even when the sun isn't shining or the wind isn't blowing.

The transition to sustainable energy is also creating new economic opportunities. Green jobs in renewable energy sectors are growing rapidly, from manufacturing and installation to maintenance and research. Countries are investing in workforce development programs to train workers for careers in the clean energy economy.

Policy initiatives are playing a crucial role in accelerating the adoption of sustainable energy. Governments worldwide are implementing carbon pricing mechanisms, renewable portfolio standards, and tax incentives to encourage investment in clean energy. International agreements are fostering collaboration on research and development of new technologies.

Despite these positive developments, challenges remain. Grid infrastructure needs to be modernized to accommodate distributed energy resources. Energy equity must be addressed to ensure that the benefits of clean energy reach all communities. And the transition must be managed carefully to support workers and communities affected by the shift away from fossil fuels.

The future of sustainable energy looks promising, with continued innovation driving down costs and improving efficiency. As technology advances and economies of scale are achieved, renewable energy is expected to become the dominant source of power worldwide, helping to mitigate climate change while powering economic growth.""",
        "source": "The New Yorker",
        "publishing_date": datetime.now() - timedelta(days=5),
        "authors": ["Alex Green", "Maria Santos"],
    },
]


class MockArticle:
    def __init__(self, data: dict):
        self._title = data["title"]
        self._url = data["url"]
        self._body = data["body"]
        self._source = data["source"]
        self._publishing_date = data["publishing_date"]
        self._authors = data.get("authors", [])  # Use get() with default empty list
        self.html = type("HTML", (), {"requested_url": data["url"]})()

    @property
    def title(self):
        return self._title

    @property
    def url(self):
        return self._url

    @property
    def body(self):
        return self._body

    @property
    def source(self):
        return self._source

    @property
    def publishing_date(self):
        return self._publishing_date

    @property
    def authors(self):
        return self._authors


def get_mock_articles(
    include_terms: List[str],
    exclude_terms: Optional[List[str]] = None,
    max_articles: Optional[int] = None,
    days_back: int = 7,
    sources: Optional[List[str]] = None,
    is_url_search: bool = False,
) -> List[Article]:
    """
    Filter and return mock articles based on search criteria.
    """
    filtered_articles = []
    cutoff_date = datetime.now() - timedelta(days=days_back)

    print(f"Mock search type: {'URL' if is_url_search else 'Body'}")

    # Normalize source names for comparison
    normalized_sources = (
        [normalize_source_name(s) for s in sources] if sources else None
    )

    for article_data in MOCK_ARTICLES:
        # Skip if article is too old
        if article_data["publishing_date"] < cutoff_date:
            print(f"Skipping article '{article_data['title']}' - too old")
            continue

        # Check source filter
        if sources:
            article_source = normalize_source_name(article_data["source"])
            if article_source not in normalized_sources:
                print(
                    f"Skipping article '{article_data['title']}' - source {article_data['source']} not in {sources}"
                )
                continue

        # Create article instance
        article = MockArticle(article_data)

        # For URL search, check terms in URL
        if is_url_search:
            url_text = article.url.lower()

            # Check include terms
            if not any(term.lower() in url_text for term in include_terms):
                continue

            # Check exclude terms
            if exclude_terms and any(
                term.lower() in url_text for term in exclude_terms
            ):
                continue
        else:
            # For body search, check terms in title and body
            text = (article.title + " " + article.body).lower()

            # Check include terms
            if not any(term.lower() in text for term in include_terms):
                continue

        filtered_articles.append(article)
        print(f"Found matching article: {article.title}")

        if max_articles and len(filtered_articles) >= max_articles:
            break

    return filtered_articles
