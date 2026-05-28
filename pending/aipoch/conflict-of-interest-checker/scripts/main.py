#!/usr/bin/env python3
"""
Conflict of Interest Checker
Check for co-authorship conflicts between authors and suggested reviewers.
"""

import argparse
import csv
import sys
from collections import defaultdict


class ConflictOfInterestChecker:
    """Check for conflicts of interest in peer review."""

    def __init__(self):
        self.author_papers = defaultdict(set)
        self.reviewer_papers = defaultdict(set)

    def load_publications(self, csv_file, name_column, paper_column):
        """Load publication records from CSV."""
        records = defaultdict(set)
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get(name_column, '').strip()
                    paper = row.get(paper_column, '').strip()
                    if name and paper:
                        records[name].add(paper)
        except FileNotFoundError:
            print(f"Error: CSV file '{csv_file}' not found.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading CSV file '{csv_file}': {e}", file=sys.stderr)
            sys.exit(1)
        return records

    def check_coauthorship_conflict(self, authors, reviewer, reviewer_papers, author_papers):
        """Check if reviewer has co-authored with any author."""
        conflicts = []

        reviewer_pubs = reviewer_papers.get(reviewer, set())

        for author in authors:
            author_pubs = author_papers.get(author, set())
            # Fix: convert to sets before intersection to support both list and set inputs
            shared_papers = set(reviewer_pubs) & set(author_pubs)

            if shared_papers:
                conflicts.append({
                    "reviewer": reviewer,
                    "author": author,
                    "shared_papers": list(shared_papers),
                    "conflict_type": "coauthorship"
                })

        return conflicts

    def check_institutional_conflict(self, reviewer_name, reviewer_institution, author_institutions):
        """Check for institutional conflicts."""
        conflicts = []
        reviewer_inst = reviewer_institution.lower()

        for author, institution in author_institutions.items():
            if institution.lower() == reviewer_inst:
                conflicts.append({
                    "reviewer": reviewer_name,  # Fix: was using undefined 'reviewer'
                    "author": author,
                    "institution": institution,
                    "conflict_type": "institutional"
                })

        return conflicts

    def check_collaboration_conflict(self, reviewer, authors, collaboration_window=4):
        """Check for recent collaboration (not implemented — stub only)."""
        # Requires publication date data; not implemented in current version
        return []

    def generate_report(self, all_conflicts):
        """Generate conflict of interest report."""
        print("\n" + "=" * 70)
        print("CONFLICT OF INTEREST REPORT")
        print("=" * 70)

        if not all_conflicts:
            print("\nNo conflicts of interest detected.")
        else:
            print(f"\nFound {len(all_conflicts)} potential conflict(s):\n")

            for i, conflict in enumerate(all_conflicts, 1):
                print(f"{i}. {conflict['conflict_type'].upper()} CONFLICT")
                print(f"   Reviewer: {conflict['reviewer']}")
                print(f"   Author: {conflict['author']}")
                if 'shared_papers' in conflict:
                    print(f"   Shared papers: {', '.join(conflict['shared_papers'][:3])}")
                if 'institution' in conflict:
                    print(f"   Institution: {conflict['institution']}")
                print()

        print("=" * 70)
        print("\nRecommendations:")
        if all_conflicts:
            print("- Exclude flagged reviewers from consideration")
            print("- Document reasons for exclusion")
            print("- Select alternative reviewers")
        else:
            print("- Proceed with reviewer selection")
            print("- Monitor for undisclosed conflicts")
        print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Conflict of Interest Checker")
    parser.add_argument("--authors", "-a", required=True,
                        help="Comma-separated author names")
    parser.add_argument("--reviewers", "-r", required=True,
                        help="Comma-separated reviewer names")
    parser.add_argument("--publications", "-p",
                        help="CSV file with publication records (columns: author, paper_id)")
    parser.add_argument("--institution",
                        help="Reviewer institution for institutional conflict check")

    args = parser.parse_args()

    checker = ConflictOfInterestChecker()

    authors = [a.strip() for a in args.authors.split(',')]
    reviewers = [r.strip() for r in args.reviewers.split(',')]

    # Load publication data if provided
    if args.publications:
        author_papers = checker.load_publications(args.publications, 'author', 'paper_id')
        reviewer_papers = checker.load_publications(args.publications, 'reviewer', 'paper_id')
    else:
        # Demo data — uses lists intentionally; set() conversion handles this in check method
        author_papers = {
            "Smith": ["paper1", "paper2", "paper3"],
            "Jones": ["paper2", "paper4"],
            "Lee": ["paper5", "paper6"]
        }
        reviewer_papers = {
            "Brown": ["paper1", "paper7"],    # Conflict with Smith
            "Davis": ["paper8", "paper9"],    # No conflict
            "Wilson": ["paper2", "paper10"]   # Conflict with Smith and Jones
        }

    # Check coauthorship conflicts
    all_conflicts = []
    for reviewer in reviewers:
        conflicts = checker.check_coauthorship_conflict(
            authors, reviewer, reviewer_papers, author_papers
        )
        all_conflicts.extend(conflicts)

    # Check institutional conflicts if --institution provided
    if args.institution:
        # Build author_institutions dict from authors list (institution applies to all authors)
        author_institutions = {author: args.institution for author in authors}
        for reviewer in reviewers:
            inst_conflicts = checker.check_institutional_conflict(
                reviewer, args.institution, author_institutions
            )
            all_conflicts.extend(inst_conflicts)

    # Generate report
    checker.generate_report(all_conflicts)


if __name__ == "__main__":
    main()
