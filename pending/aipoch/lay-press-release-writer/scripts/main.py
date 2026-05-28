#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lay Press Release Writer
Convert academic papers into university newsroom style press releases

Usage:
    python main.py --paper-text "Paper content..." [options]"""

import argparse
import json
import sys
import re
from datetime import datetime
from typing import Dict, List, Optional


def extract_key_findings(text: str) -> List[str]:
    """Extract key findings from the paper"""
    findings = []
    
    # Find the conclusion section
    conclusion_patterns = [
        '(?:conclusion|conclusion|findings|results).*?(?:\\n|$)(.*?)(?:\\n\\n|\\Z)',
        '(?:This article|We|This research).*?(?:Discover|Prove|Show|Reveal)(.*?)(?:.|;)',
    ]
    
    for pattern in conclusion_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches[:3]:  # Limit to 3 discoveries
            finding = match.strip()
            if len(finding) > 20 and len(finding) < 500:
                findings.append(finding)
    
    return findings[:3]  # Return to top 3 key findings


def generate_headline(title: str, key_finding: str) -> str:
    """Generate compelling headlines"""
    # Simplify the title to make it more newsy
    headline = title
    
    # Remove overly academic terms
    academic_terms = ['Research', 'analyze', 'Discuss', 'based on', 'method', 'Model']
    for term in academic_terms:
        headline = headline.replace(term, '')
    
    # Add news terms
    news_boosters = ['breakthrough', 'new discovery', 'first', 'Innovation', 'important progress']
    
    # If these words are not in the title, add them appropriately
    if not any(word in headline for word in news_boosters):
        if 'first' in key_finding or 'first' in title:
            headline = f"major breakthrough：{headline}"
        elif len(headline) < 15:
            headline = f"research reveals：{headline}"
    
    return headline.strip()


def generate_subheadline(key_findings: List[str], institution: str) -> str:
    """Generate subtitle"""
    if key_findings:
        finding = key_findings[0]
        # Simplified into one sentence
        finding = finding[:80] + '...' if len(finding) > 80 else finding
        return f"{institution}research team{finding}"
    return f"{institution}Latest research results released"


def generate_lead(title: str, authors: List[str], institution: str, 
                  venue: str, key_findings: List[str]) -> str:
    """Generate introduction (first paragraph) - the most important part of the inverted pyramid structure"""
    author_str = '、'.join(authors[:3]) if authors else 'research team'
    if len(authors) > 3:
        author_str += 'wait'
    
    lead = f"【Place】{institution}{author_str}"
    
    if venue:
        lead += f"exist《{venue}》latest research published"
    else:
        lead += "latest research"
    
    if key_findings:
        finding = key_findings[0]
        # Simplify discovery descriptions
        finding = re.sub(r'[（(].*?[)）]', '', finding)  # Remove bracket content
        finding = finding[:100] + '...' if len(finding) > 100 else finding
        lead += f"{finding}。"
    else:
        lead += "Made important progress."
    
    return lead


def generate_body(text: str, key_findings: List[str], target_audience: str) -> str:
    """Generate body content"""
    paragraphs = []
    
    # Paragraph 1: Research background
    background = extract_background(text)
    if background:
        paragraphs.append(f"Research background：{background}")
    
    # Paragraph 2: Core findings
    if key_findings:
        findings_text = "Key findings from the study include:"
        for i, finding in enumerate(key_findings, 1):
            simplified = simplify_language(finding)
            findings_text += f"{i}) {simplified}；"
        paragraphs.append(findings_text)
    
    # Paragraph 3: Meaning and Application
    significance = extract_significance(text)
    if significance:
        paragraphs.append(f"Research significance：{significance}")
    
    return '\n\n'.join(paragraphs)


def generate_quotes(authors: List[str], text: str) -> List[str]:
    """Generate researcher quotes"""
    quotes = []
    
    if authors:
        first_author = authors[0]
        quotes.append(f"\"This research provides a new perspective on our understanding of the field，\"{first_author}English，\"We expect this discovery to bring practical value to related applications。\"")
    
    if len(authors) > 1:
        quotes.append(f"\"This is the result of many years of teamwork，\"The collaborators added，\"In the future, we will continue to explore this direction in depth。\"")
    
    return quotes


def extract_background(text: str) -> str:
    """Extract research background"""
    patterns = [
        '(?:Background|background|introduction|Introduction).*?(?:\\n|$)(.*?)(?:\\n\\n|\\Z)',
        '(?:With|In recent years|Currently).*?(?:Development|Progress|Challenges|Problems).*?(?:.;)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            bg = match.group(1).strip()
            # Simplified background description
            bg = simplify_language(bg)
            return bg[:200] + '...' if len(bg) > 200 else bg
    
    return "This research provides an in-depth exploration of important current issues in the field."


def extract_significance(text: str) -> str:
    """Extract research significance"""
    patterns = [
        '(?:significance|implications|impact).*?(?:\\n|$)(.*?)(?:\\n\\n|\\Z)',
        '(?:this research|this research).*?(?:helps|can|can|for).*?(?:.;)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            sig = match.group(1).strip()
            sig = simplify_language(sig)
            return sig[:200] + '...' if len(sig) > 200 else sig
    
    return "This research provides important theoretical foundation and practical guidance for the development of related fields."


def simplify_language(text: str) -> str:
    """Simplify academic language into colloquial language"""
    # Mapping academic vocabulary to popular vocabulary
    replacements = {
        'This article': 'The study',
        'Based on this': 'On this basis',
        'In summary': 'in general',
        'Research shows': 'research findings',
        'proved': 'Discover',
        'revealed': 'showed',
        'Built': 'developed',
        'proposed': 'proposed',
        'Realized': 'Achieved',
        'Optimized': 'improved',
        'Significantly': 'obvious',
        ' methodology': 'method',
        ' algorithm': 'algorithm',
        ' framework': 'frame',
    }
    
    for academic, lay in replacements.items():
        text = text.replace(academic, lay)
    
    return text


def generate_boilerplate(institution: str) -> str:
    """Introduction to generating institutions"""
    templates = {
        'Tsinghua University': 'Tsinghua University is a famous institution of higher learning in China and an important base for high-level talent training and scientific and technological research in China.',
        'Beijing University': 'Peking University is China\'s first national comprehensive university, the center of the New Culture Movement and the birthplace of the May Fourth Movement.',
        'Fudan University': 'Fudan University is the first institution of higher learning independently founded by the Chinese. It is a world-renowned and domestic top comprehensive research university.',
        'Shanghai Jiao Tong University': 'Shanghai Jiao Tong University is a national key university directly under the Ministry of Education and jointly established with Shanghai Municipality. It is a "comprehensive, research-oriented, international" domestic first-class and internationally renowned university.',
    }
    
    return templates.get(institution, 
        f'{institution}It is an institution of higher learning dedicated to teaching and scientific research.，Have important influence in multiple disciplines。')


def generate_media_contact(institution: str) -> Dict:
    """Generate media contact information"""
    return {
        "department": f"{institution}News Center",
        "email": f"media@{institution.lower().replace('University', '').replace('college', '')}.edu.cn",
        "phone": "Please contact the school switchboard and transfer to the News Center"
    }


def write_press_release(args) -> Dict:
    """Main function: Generate press release"""
    
    # Parse parameters
    paper_text = args.paper_text or ""
    paper_title = args.paper_title or "Important research results"
    authors = args.authors.split(',') if args.authors else []
    institution = args.institution or "Our school"
    venue = args.publication_venue or ""
    target_audience = args.target_audience or "general"
    
    # Extract key information
    key_findings = extract_key_findings(paper_text)
    
    # Generate press release parts
    headline = generate_headline(paper_title, key_findings[0] if key_findings else "")
    subheadline = generate_subheadline(key_findings, institution)
    dateline = f"{institution}，{datetime.now().strftime('%Y year %m month %d day')}"
    lead = generate_lead(paper_title, authors, institution, venue, key_findings)
    body = generate_body(paper_text, key_findings, target_audience)
    quotes = generate_quotes(authors, paper_text)
    boilerplate = generate_boilerplate(institution)
    media_contact = generate_media_contact(institution)
    
    # Assembly output
    press_release = {
        "headline": headline,
        "subheadline": subheadline,
        "dateline": dateline,
        "lead": lead,
        "body": body,
        "quotes": quotes,
        "boilerplate": boilerplate,
        "media_contact": media_contact
    }
    
    return press_release


def main():
    parser = argparse.ArgumentParser(
        description='Convert academic papers into university newsroom style press releases'
    )
    
    parser.add_argument('--paper-text', type=str, required=True,
                        help='Full text or abstract text of the paper')
    parser.add_argument('--paper-title', type=str, default='',
                        help='Paper title')
    parser.add_argument('--authors', type=str, default='',
                        help='List of authors, separated by commas')
    parser.add_argument('--institution', type=str, default='',
                        help='Affiliated institution/university name')
    parser.add_argument('--publication-venue', type=str, default='',
                        help='Publication journal/conference name')
    parser.add_argument('--target-audience', type=str, default='general',
                        choices=['general', 'alumni', 'media'],
                        help='target audience')
    parser.add_argument('--tone', type=str, default='formal',
                        choices=['formal', 'friendly', 'inspiring'],
                        help='tone style')
    parser.add_argument('--output', type=str, default='',
                        help='Output file path (JSON format)')
    
    args = parser.parse_args()
    
    # Generate press release
    result = write_press_release(args)
    
    # Formatted output
    formatted_output = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(formatted_output)
        print(f"Press release saved to: {args.output}")
    else:
        print(formatted_output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
