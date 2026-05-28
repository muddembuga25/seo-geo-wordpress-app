"""
SEO Analyzer Module for SEO-GEO WordPress App
Analyzes content for SEO optimization and provides recommendations.
"""

import re
from typing import Dict, List, Tuple, Any


class SEOAnalyzer:
    """Analyzes blog post content for SEO quality and provides scores."""
    
    def __init__(self):
        """Initialize the SEO analyzer."""
        self.min_word_count = 300
        self.ideal_word_count = 1500
        self.max_word_count = 3000
        self.optimal_keyword_density = (0.5, 2.5)  # percentage
        self.max_title_length = 60
        self.max_description_length = 160
    
    def analyze(self, title: str, content: str, meta_description: str = "",
                keyword: str = "") -> Dict[str, Any]:
        """Perform full SEO analysis on the content."""
        results = {
            "overall_score": 0,
            "title_analysis": {},
            "content_analysis": {},
            "meta_analysis": {},
            "keyword_analysis": {},
            "recommendations": [],
            "passed_checks": [],
        }
        
        results["title_analysis"] = self._analyze_title(title, keyword)
        results["content_analysis"] = self._analyze_content(content)
        results["meta_analysis"] = self._analyze_meta(meta_description)
        results["keyword_analysis"] = self._analyze_keyword_usage(
            title, content, meta_description, keyword
        )
        
        results["overall_score"] = self._calculate_overall_score(results)
        results["recommendations"] = self._generate_recommendations(results)
        results["passed_checks"] = self._get_passed_checks(results)
        
        return results
    
    def _analyze_title(self, title: str, keyword: str) -> Dict[str, Any]:
        """Analyze the post title for SEO."""
        title = title.strip()
        length = len(title)
        words = title.split()
        
        result = {
            "score": 100,
            "length": length,
            "word_count": len(words),
            "issues": [],
            "passed": [],
        }
        
        if length == 0:
            result["score"] -= 100
            result["issues"].append("Title is empty")
        else:
            if length > self.max_title_length:
                result["score"] -= 20
                result["issues"].append(
                    f"Title too long ({length} chars). Max recommended: {self.max_title_length}"
                )
            elif length < 30:
                result["score"] -= 10
                result["issues"].append(
                    "Title too short. Aim for 30-60 characters"
                )
            else:
                result["passed"].append("Title length optimal")
            
            if any(c.isupper() for c in title[1:]) and title != title.lower():
                result["passed"].append("Title uses proper capitalization")
            
            if keyword and keyword.lower() in title.lower():
                result["score"] += 10
                result["passed"].append("Keyword found in title")
            elif keyword:
                result["score"] -= 20
                result["issues"].append("Keyword not found in title")
        
        result["score"] = max(0, min(100, result["score"]))
        return result
    
    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze the post content for SEO."""
        content = content.strip()
        words = re.findall(r'\b\w+\b', content.lower())
        sentences = re.split(r'[.!?]+', content)
        paragraphs = content.split('\n\n')
        
        word_count = len(words)
        
        result = {
            "score": 100,
            "word_count": word_count,
            "sentence_count": len([s for s in sentences if s.strip()]),
            "paragraph_count": len([p for p in paragraphs if p.strip()]),
            "issues": [],
            "passed": [],
        }
        
        if word_count == 0:
            result["score"] -= 100
            result["issues"].append("Content is empty")
        else:
            if word_count < self.min_word_count:
                result["score"] -= 30
                result["issues"].append(
                    f"Content too short ({word_count} words). "
                    f"Minimum: {self.min_word_count} words"
                )
            elif word_count > self.max_word_count:
                result["score"] -= 10
                result["issues"].append(
                    f"Content very long ({word_count} words). "
                    f"Consider breaking into series"
                )
            else:
                result["passed"].append(
                    f"Word count ({word_count}) within good range"
                )
            
            if len(paragraphs) < 3:
                result["score"] -= 15
                result["issues"].append(
                    "Too few paragraphs. Content should have at least 3"
                )
            else:
                result["passed"].append("Good paragraph structure")
            
            headings = re.findall(r'^#+\s+', content, re.MULTILINE)
            if headings:
                result["passed"].append(f"Found {len(headings)} headings")
                result["heading_count"] = len(headings)
            else:
                result["score"] -= 10
                result["issues"].append(
                    "No headings found. Add H2/H3 headings for better structure"
                )
            
            avg_sentence = (word_count / result["sentence_count"]
                           if result["sentence_count"] > 0 else 0)
            if avg_sentence > 30:
                result["score"] -= 10
                result["issues"].append(
                    "Sentences are too long. Use shorter sentences"
                )
            else:
                result["passed"].append("Readability score good")
        
        result["score"] = max(0, min(100, result["score"]))
        return result
    
    def _analyze_meta(self, meta_description: str) -> Dict[str, Any]:
        """Analyze the meta description for SEO."""
        meta = meta_description.strip()
        length = len(meta)
        
        result = {
            "score": 100 if meta else 0,
            "length": length,
            "issues": [],
            "passed": [],
        }
        
        if not meta:
            result["issues"].append(
                "Meta description is empty. Add a description (120-160 chars)"
            )
        else:
            if length > self.max_description_length:
                result["score"] -= 20
                result["issues"].append(
                    f"Meta description too long ({length} chars). "
                    f"Max: {self.max_description_length}"
                )
            elif length < 120:
                result["score"] -= 10
                result["issues"].append(
                    f"Meta description too short ({length} chars). "
                    f"Aim for 120-160 characters"
                )
            else:
                result["passed"].append("Meta description length optimal")
        
        result["score"] = max(0, min(100, result["score"]))
        return result
    
    def _analyze_keyword_usage(self, title: str, content: str,
                               meta: str, keyword: str) -> Dict[str, Any]:
        """Analyze keyword usage in the content."""
        result = {
            "score": 100,
            "keyword": keyword,
            "issues": [],
            "passed": [],
        }
        
        if not keyword:
            result["issues"].append("No keyword provided for analysis")
            return result
        
        keyword_lower = keyword.lower()
        
        content_lower = content.lower()
        content_words = re.findall(r'\b\w+\b', content_lower)
        total_words = len(content_words)
        
        keyword_count = 0
        for word in content_words:
            if keyword_lower in word or word in keyword_lower:
                keyword_count += 1
        
        exact_count = content_lower.count(keyword_lower)
        
        density = (keyword_count / total_words * 100) if total_words > 0 else 0
        exact_density = (exact_count / total_words * 100) if total_words > 0 else 0
        
        result["keyword_count"] = keyword_count
        result["exact_count"] = exact_count
        result["density"] = round(density, 2)
        result["exact_density"] = round(exact_density, 2)
        
        if keyword_count == 0:
            result["score"] -= 40
            result["issues"].append("Keyword not found in content")
        else:
            min_d, max_d = self.optimal_keyword_density
            if density < min_d:
                result["score"] -= 15
                result["issues"].append(
                    f"Keyword density too low ({density:.1f}%). "
                    f"Aim for {min_d}-{max_d}%"
                )
            elif density > max_d:
                result["score"] -= 20
                result["issues"].append(
                    f"Keyword density too high ({density:.1f}%). "
                    f"Aim for {min_d}-{max_d}% - avoid stuffing"
                )
            else:
                result["passed"].append(
                    f"Keyword density optimal ({density:.1f}%)"
                )
        
        if keyword_lower in title.lower():
            result["passed"].append("Keyword in title")
        if keyword_lower in meta.lower():
            result["passed"].append("Keyword in meta description")
        
        if exact_count > 5:
            result["score"] -= 10
            result["issues"].append(
                "Too many exact-match keywords. Use variations"
            )
        
        result["score"] = max(0, min(100, result["score"]))
        return result
    
    def _calculate_overall_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall SEO score."""
        scores = [
            results["title_analysis"]["score"],
            results["content_analysis"]["score"],
            results["meta_analysis"]["score"],
            results["keyword_analysis"]["score"],
        ]
        return int(sum(scores) / len(scores))
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[Dict]:
        """Generate actionable SEO recommendations."""
        recommendations = []
        
        for section in ["title_analysis", "content_analysis",
                        "meta_analysis", "keyword_analysis"]:
            issues = results[section].get("issues", [])
            for issue in issues:
                recommendations.append({
                    "section": section,
                    "issue": issue,
                    "severity": "high" if results[section]["score"] < 50
                                else "medium" if results[section]["score"] < 75
                                else "low"
                })
        
        recommendations.sort(key=lambda x:
            {"high": 0, "medium": 1, "low": 2}[x["severity"]])
        
        return recommendations
    
    def _get_passed_checks(self, results: Dict[str, Any]) -> List[Dict]:
        """Get all passed SEO checks."""
        passed = []
        for section in ["title_analysis", "content_analysis",
                        "meta_analysis", "keyword_analysis"]:
            checks = results[section].get("passed", [])
            for check in checks:
                passed.append({"section": section, "check": check})
        return passed
    
    def get_score_grade(self, score: int) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        return "F"


if __name__ == "__main__":
    analyzer = SEOAnalyzer()
    sample_title = "Best SEO Tips for 2026"
    sample_content = """SEO is important for your website.

## Getting Started with SEO

Search engine optimization helps your site rank higher.
"""
    sample_meta = "Learn the best SEO tips for 2026"
    results = analyzer.analyze(sample_title, sample_content, sample_meta,
                               keyword="SEO")
    print(f"Overall Score: {results['overall_score']} - {analyzer.get_score_grade(results['overall_score'])}")
