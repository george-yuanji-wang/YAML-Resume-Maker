#!/usr/bin/env python3
"""
Author: George Yuanji Wang
Version: 1.0.0
"""

import yaml
import sys
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class ResumeGenerator:
    
    def __init__(self, yaml_file, output_dir="output"):
        self.yaml_file = Path(yaml_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Load and validate YAML data
        self.data = self._load_yaml()
        
        # Load configuration
        self.config = self._load_config()
        
        # Setup styles
        self.styles = self._create_styles()
        
        # Story elements (content to be rendered)
        self.story = []
        
    def _load_yaml(self):
        """Load and validate YAML data."""
        try:
            with open(self.yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                raise ValueError("YAML file is empty")
            
            # Validate required fields
            if 'personal' not in data:
                raise ValueError("Missing required 'personal' section")
            
            personal = data['personal']
            if 'name' not in personal:
                raise ValueError("Missing required 'name' field in personal section")
            
            return data
            
        except FileNotFoundError:
            print(f"Error: YAML file '{self.yaml_file}' not found")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            sys.exit(1)
        except ValueError as e:
            print(f"Validation error: {e}")
            sys.exit(1)
    
    def _load_config(self):
        config = self.data.get('config', {})
        
        # Font configuration
        fonts = config.get('fonts', {})
        default_config = {
            'font_name': fonts.get('name', 'Helvetica'),
            'font_name_bold': fonts.get('name_bold', 'Helvetica-Bold'),
            'font_name_italic': fonts.get('name_italic', 'Helvetica-Oblique'),
            'name_size': fonts.get('name_size', 20),
            'section_header_size': fonts.get('section_header_size', 12),
            'title_size': fonts.get('title_size', 10),
            'body_size': fonts.get('body_size', 9),
            
            # Spacing configuration
            'margin': config.get('margin', 0.6),  # in inches
            'section_spacing': config.get('section_spacing', 0.08),  # in inches
            'item_spacing': config.get('item_spacing', 0.06),  # in inches
            
            # Section order configuration
            'section_order': config.get('section_order', [
                'summary',
                'experience',
                'education',
                'skills',
                'projects',
                'certifications',
                'awards',
                'publications',
                'languages',
                'volunteer'
            ]),
            
            # Footer
            'footer': config.get('footer', False)
        }
        
        return default_config
    
    def _create_styles(self):
        styles = getSampleStyleSheet()
        
        # Get config values
        font = self.config['font_name']
        font_bold = self.config['font_name_bold']
        font_italic = self.config['font_name_italic']
        
        # Name style (large, bold, centered)
        styles.add(ParagraphStyle(
            name='Name',
            parent=styles['Heading1'],
            fontSize=self.config['name_size'],
            textColor=colors.HexColor('#000000'),
            spaceAfter=4,
            alignment=TA_CENTER,
            fontName=font_bold
        ))
        
        # Contact info style
        styles.add(ParagraphStyle(
            name='Contact',
            parent=styles['Normal'],
            fontSize=self.config['body_size'],
            textColor=colors.HexColor('#333333'),
            alignment=TA_CENTER,
            spaceAfter=8
        ))
        
        # Section header style
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=self.config['section_header_size'],
            textColor=colors.HexColor('#000000'),
            spaceAfter=4,
            spaceBefore=8,
            fontName=font_bold,
            borderWidth=0,
            borderPadding=0,
            leading=14
        ))
        
        # Job title / degree style
        styles.add(ParagraphStyle(
            name='ItemTitle',
            parent=styles['Normal'],
            fontSize=self.config['title_size'],
            textColor=colors.HexColor('#000000'),
            fontName=font_bold,
            spaceAfter=1,
            leading=12
        ))
        
        # Company / institution style
        styles.add(ParagraphStyle(
            name='ItemSubtitle',
            parent=styles['Normal'],
            fontSize=self.config['body_size'],
            textColor=colors.HexColor('#333333'),
            fontName=font_italic,
            spaceAfter=1,
            leading=11
        ))
        
        # Date range style
        styles.add(ParagraphStyle(
            name='DateRange',
            parent=styles['Normal'],
            fontSize=self.config['body_size'],
            textColor=colors.HexColor('#666666'),
            alignment=TA_RIGHT,
            leading=11
        ))
        
        # Body text / bullet points
        styles.add(ParagraphStyle(
            name='ResumeBody',
            parent=styles['Normal'],
            fontSize=self.config['body_size'],
            textColor=colors.HexColor('#000000'),
            spaceAfter=2,
            leading=12,
            leftIndent=0,
            bulletIndent=10
        ))
        
        # Summary text
        styles.add(ParagraphStyle(
            name='Summary',
            parent=styles['Normal'],
            fontSize=self.config['body_size'],
            textColor=colors.HexColor('#000000'),
            spaceAfter=4,
            leading=12,
            alignment=TA_JUSTIFY
        ))
        
        # Skill items
        styles.add(ParagraphStyle(
            name='SkillItem',
            parent=styles['Normal'],
            fontSize=self.config['body_size'],
            textColor=colors.HexColor('#000000'),
            spaceAfter=2,
            leading=11
        ))
        
        # Footer style
        styles.add(ParagraphStyle(
            name='Footer',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.HexColor('#999999'),
            alignment=TA_CENTER,
            leading=9
        ))
        
        return styles
    
    def _add_section_header(self, title):
        self.story.append(Paragraph(title, self.styles['SectionHeader']))
        # Add a subtle line under the header
        self.story.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor('#000000'),
            spaceAfter=4
        ))
    
    def _format_date_range(self, start_date, end_date=None, present=False):
        if not start_date:
            return ""
        
        # Handle different date formats
        if isinstance(start_date, str):
            start = start_date
        else:
            start = str(start_date)
        
        if present or (end_date and str(end_date).lower() == 'present'):
            return f"{start} - Present"
        elif end_date:
            if isinstance(end_date, str):
                end = end_date
            else:
                end = str(end_date)
            return f"{start} - {end}"
        else:
            return start
    
    def _build_header(self):
        personal = self.data.get('personal', {})
        
        # Name
        name = personal.get('name', '')
        self.story.append(Paragraph(name, self.styles['Name']))
        
        # Contact information
        contact_parts = []
        
        if 'email' in personal:
            contact_parts.append(personal['email'])
        
        if 'phone' in personal:
            contact_parts.append(personal['phone'])
        
        if 'location' in personal:
            location = personal['location']
            if isinstance(location, dict):
                loc_parts = []
                if 'city' in location:
                    loc_parts.append(location['city'])
                if 'state' in location:
                    loc_parts.append(location['state'])
                if 'country' in location:
                    loc_parts.append(location['country'])
                contact_parts.append(', '.join(loc_parts))
            else:
                contact_parts.append(str(location))
        
        if contact_parts:
            contact_text = ' • '.join(contact_parts)
            self.story.append(Paragraph(contact_text, self.styles['Contact']))
        
        # Links (LinkedIn, GitHub, Portfolio, etc.)
        links = personal.get('links', {})
        if links:
            link_parts = []
            for key, value in links.items():
                if value:
                    # Create a simple text representation (not hyperlinked in black/white)
                    link_parts.append(f"{key.title()}: {value}")
            
            if link_parts:
                links_text = ' • '.join(link_parts)
                self.story.append(Paragraph(links_text, self.styles['Contact']))
        
        self.story.append(Spacer(1, self.config["section_spacing"]*inch))
    
    def _build_summary(self):
        if 'summary' not in self.data:
            return
        
        summary = self.data['summary']
        if isinstance(summary, str):
            summary_text = summary
        elif isinstance(summary, list):
            summary_text = ' '.join(summary)
        else:
            return
        
        if summary_text:
            self._add_section_header('PROFESSIONAL SUMMARY')
            self.story.append(Paragraph(summary_text, self.styles['Summary']))
            self.story.append(Spacer(1, self.config["item_spacing"]*inch))
    
    def _build_experience(self):
        if 'experience' not in self.data:
            return
        
        experiences = self.data['experience']
        if not experiences:
            return
        
        self._add_section_header('PROFESSIONAL EXPERIENCE')
        
        for i, exp in enumerate(experiences):
            if i > 0:
                self.story.append(Spacer(1, self.config["item_spacing"]*inch))
            
            # Create a table for title and date alignment
            title = exp.get('title', '')
            company = exp.get('company', '')
            
            # Date range
            date_range = self._format_date_range(
                exp.get('start_date'),
                exp.get('end_date'),
                exp.get('present', False)
            )
            
            # Location
            location = exp.get('location', '')
            
            # Title row
            title_data = [[
                Paragraph(title, self.styles['ItemTitle']),
                Paragraph(date_range, self.styles['DateRange'])
            ]]
            
            title_table = Table(title_data, colWidths=[4.5*inch, 2*inch])
            title_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            self.story.append(title_table)
            
            # Company and location
            if company:
                company_location = company
                if location:
                    company_location += f" • {location}"
                self.story.append(Paragraph(company_location, self.styles['ItemSubtitle']))
            
            # Description or highlights
            if 'description' in exp and exp['description']:
                self.story.append(Spacer(1, 0.03*inch))
                self.story.append(Paragraph(exp['description'], self.styles['ResumeBody']))
            
            # Achievements/responsibilities as bullet points
            if 'highlights' in exp:
                highlights = exp['highlights']
                if highlights:
                    self.story.append(Spacer(1, 0.03*inch))
                    for highlight in highlights:
                        if highlight and highlight.strip():  # Skip empty/whitespace-only
                            bullet_text = f"• {highlight}"
                            self.story.append(Paragraph(bullet_text, self.styles['ResumeBody']))
        
        self.story.append(Spacer(1, self.config["section_spacing"]*inch))
    
    def _build_education(self):
        if 'education' not in self.data:
            return
        
        education = self.data['education']
        if not education:
            return
        
        self._add_section_header('EDUCATION')
        
        for i, edu in enumerate(education):
            if i > 0:
                self.story.append(Spacer(1, self.config["item_spacing"]*inch))
            
            # Degree and date
            degree = edu.get('degree', '')
            field = edu.get('field', '')
            if degree and field:
                degree_text = f"{degree} in {field}"
            elif degree:
                degree_text = degree
            elif field:
                degree_text = field
            else:
                degree_text = ''
            
            date_range = self._format_date_range(
                edu.get('start_date'),
                edu.get('end_date'),
                edu.get('present', False)
            )
            
            if degree_text:
                degree_data = [[
                    Paragraph(degree_text, self.styles['ItemTitle']),
                    Paragraph(date_range, self.styles['DateRange'])
                ]]
                
                degree_table = Table(degree_data, colWidths=[4.5*inch, 2*inch])
                degree_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]))
                
                self.story.append(degree_table)
            
            # Institution and location
            institution = edu.get('institution', '')
            location = edu.get('location', '')
            
            if institution:
                inst_location = institution
                if location:
                    inst_location += f" • {location}"
                self.story.append(Paragraph(inst_location, self.styles['ItemSubtitle']))
            
            # GPA, honors, etc.
            details = []
            if 'gpa' in edu:
                details.append(f"GPA: {edu['gpa']}")
            if 'honors' in edu:
                details.append(edu['honors'])
            
            if details:
                details_text = ' • '.join(details)
                self.story.append(Paragraph(details_text, self.styles['ResumeBody']))
            
            # Additional highlights
            if 'highlights' in edu:
                highlights = edu['highlights']
                if highlights:
                    for highlight in highlights:
                        bullet_text = f"• {highlight}"
                        self.story.append(Paragraph(bullet_text, self.styles['ResumeBody']))
        
        self.story.append(Spacer(1, self.config["section_spacing"]*inch))
    
    def _build_skills(self):
        if 'skills' not in self.data:
            return
        
        skills = self.data['skills']
        if not skills:
            return
        
        self._add_section_header('SKILLS')
        
        # Handle different skill formats
        if isinstance(skills, dict):
            # Categorized skills
            for category, skill_list in skills.items():
                if skill_list:
                    category_title = f"<b>{category}:</b> "
                    if isinstance(skill_list, list):
                        skills_text = ', '.join(skill_list)
                    else:
                        skills_text = str(skill_list)
                    
                    full_text = category_title + skills_text
                    self.story.append(Paragraph(full_text, self.styles['SkillItem']))
        
        elif isinstance(skills, list):
            # Simple list of skills
            skills_text = ', '.join(skills)
            self.story.append(Paragraph(skills_text, self.styles['SkillItem']))
        
        self.story.append(Spacer(1, self.config["section_spacing"]*inch))
    
    def _build_projects(self):
        if 'projects' not in self.data:
            return
        
        projects = self.data['projects']
        if not projects:
            return
        
        self._add_section_header('PROJECTS')
        
        for i, project in enumerate(projects):
            if i > 0:
                self.story.append(Spacer(1, self.config["item_spacing"]*inch))
            
            # Project name and date
            name = project.get('name', '')
            date = project.get('date', '')
            
            if name:
                name_data = [[
                    Paragraph(name, self.styles['ItemTitle']),
                    Paragraph(date, self.styles['DateRange'])
                ]]
                
                name_table = Table(name_data, colWidths=[4.5*inch, 2*inch])
                name_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]))
                
                self.story.append(name_table)
            
            # Technologies/tools
            if 'technologies' in project:
                tech = project['technologies']
                if isinstance(tech, list):
                    tech_text = ', '.join(tech)
                else:
                    tech_text = str(tech)
                self.story.append(Paragraph(f"<i>Technologies:</i> {tech_text}", self.styles['ItemSubtitle']))
            
            # Description
            if 'description' in project:
                self.story.append(Spacer(1, 0.03*inch))
                self.story.append(Paragraph(project['description'], self.styles['ResumeBody']))
            
            # Highlights
            if 'highlights' in project:
                highlights = project['highlights']
                if highlights:
                    self.story.append(Spacer(1, 0.03*inch))
                    for highlight in highlights:
                        bullet_text = f"• {highlight}"
                        self.story.append(Paragraph(bullet_text, self.styles['ResumeBody']))
            
            # URL
            if 'url' in project:
                url_text = f"<i>Link:</i> {project['url']}"
                self.story.append(Paragraph(url_text, self.styles['ResumeBody']))
        
        self.story.append(Spacer(1, self.config["section_spacing"]*inch))
    
    def _build_certifications(self):
        if 'certifications' not in self.data:
            return
        
        certifications = self.data['certifications']
        if not certifications:
            return
        
        self._add_section_header('CERTIFICATIONS')
        
        for cert in certifications:
            name = cert.get('name', '')
            issuer = cert.get('issuer', '')
            date = cert.get('date', '')
            
            # Certification name and date
            if name:
                cert_data = [[
                    Paragraph(name, self.styles['ItemTitle']),
                    Paragraph(date, self.styles['DateRange'])
                ]]
                
                cert_table = Table(cert_data, colWidths=[4.5*inch, 2*inch])
                cert_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]))
                
                self.story.append(cert_table)
            
            if issuer:
                self.story.append(Paragraph(issuer, self.styles['ItemSubtitle']))
            
            if 'credential_id' in cert:
                cred_text = f"Credential ID: {cert['credential_id']}"
                self.story.append(Paragraph(cred_text, self.styles['ResumeBody']))
            
            self.story.append(Spacer(1, 0.04*inch))
        
        self.story.append(Spacer(1, 0.03*inch))
    
    def _build_awards(self):
        if 'awards' not in self.data:
            return
        
        awards = self.data['awards']
        if not awards:
            return
        
        self._add_section_header('AWARDS & HONORS')
        
        for award in awards:
            name = award.get('name', '')
            issuer = award.get('issuer', '')
            date = award.get('date', '')
            
            if name:
                award_data = [[
                    Paragraph(name, self.styles['ItemTitle']),
                    Paragraph(date, self.styles['DateRange'])
                ]]
                
                award_table = Table(award_data, colWidths=[4.5*inch, 2*inch])
                award_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]))
                
                self.story.append(award_table)
            
            if issuer:
                self.story.append(Paragraph(issuer, self.styles['ItemSubtitle']))
            
            if 'description' in award:
                self.story.append(Paragraph(award['description'], self.styles['ResumeBody']))
            
            self.story.append(Spacer(1, 0.04*inch))
        
        self.story.append(Spacer(1, 0.03*inch))
    
    def _build_publications(self):
        if 'publications' not in self.data:
            return
        
        publications = self.data['publications']
        if not publications:
            return
        
        self._add_section_header('PUBLICATIONS')
        
        for pub in publications:
            title = pub.get('title', '')
            authors = pub.get('authors', '')
            venue = pub.get('venue', '')
            date = pub.get('date', '')
            
            if title:
                self.story.append(Paragraph(f"<b>{title}</b>", self.styles['ItemTitle']))
            
            if authors:
                if isinstance(authors, list):
                    authors_text = ', '.join(authors)
                else:
                    authors_text = str(authors)
                self.story.append(Paragraph(authors_text, self.styles['ResumeBody']))
            
            venue_date = []
            if venue:
                venue_date.append(venue)
            if date:
                venue_date.append(date)
            
            if venue_date:
                venue_text = ', '.join(venue_date)
                self.story.append(Paragraph(f"<i>{venue_text}</i>", self.styles['ItemSubtitle']))
            
            if 'doi' in pub:
                doi_text = f"DOI: {pub['doi']}"
                self.story.append(Paragraph(doi_text, self.styles['ResumeBody']))
            
            self.story.append(Spacer(1, 0.04*inch))
        
        self.story.append(Spacer(1, 0.03*inch))
    
    def _build_languages(self):
        if 'languages' not in self.data:
            return
        
        languages = self.data['languages']
        if not languages:
            return
        
        self._add_section_header('LANGUAGES')
        
        if isinstance(languages, dict):
            # Languages with proficiency levels
            lang_items = []
            for lang, level in languages.items():
                lang_items.append(f"{lang} ({level})")
            lang_text = ', '.join(lang_items)
            self.story.append(Paragraph(lang_text, self.styles['SkillItem']))
        
        elif isinstance(languages, list):
            # Simple list
            for lang in languages:
                if isinstance(lang, dict):
                    name = lang.get('name', '')
                    level = lang.get('level', '')
                    if name:
                        lang_text = f"{name}"
                        if level:
                            lang_text += f" ({level})"
                        self.story.append(Paragraph(f"• {lang_text}", self.styles['ResumeBody']))
                else:
                    self.story.append(Paragraph(f"• {lang}", self.styles['ResumeBody']))
        
        self.story.append(Spacer(1, self.config["section_spacing"]*inch))
    
    def _build_volunteer(self):
        if 'volunteer' not in self.data:
            return
        
        volunteer = self.data['volunteer']
        if not volunteer:
            return
        
        self._add_section_header('VOLUNTEER EXPERIENCE')
        
        for i, vol in enumerate(volunteer):
            if i > 0:
                self.story.append(Spacer(1, self.config["item_spacing"]*inch))
            
            # Role and date
            role = vol.get('role', '')
            organization = vol.get('organization', '')
            date_range = self._format_date_range(
                vol.get('start_date'),
                vol.get('end_date'),
                vol.get('present', False)
            )
            
            if role:
                role_data = [[
                    Paragraph(role, self.styles['ItemTitle']),
                    Paragraph(date_range, self.styles['DateRange'])
                ]]
                
                role_table = Table(role_data, colWidths=[4.5*inch, 2*inch])
                role_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]))
                
                self.story.append(role_table)
            
            if organization:
                self.story.append(Paragraph(organization, self.styles['ItemSubtitle']))
            
            # Description
            if 'description' in vol:
                self.story.append(Spacer(1, 0.03*inch))
                self.story.append(Paragraph(vol['description'], self.styles['ResumeBody']))
            
            # Highlights
            if 'highlights' in vol:
                highlights = vol['highlights']
                if highlights:
                    self.story.append(Spacer(1, 0.03*inch))
                    for highlight in highlights:
                        bullet_text = f"• {highlight}"
                        self.story.append(Paragraph(bullet_text, self.styles['ResumeBody']))
        
        self.story.append(Spacer(1, self.config["section_spacing"]*inch))
    
    def generate(self):
        # Determine output filename
        personal = self.data.get('personal', {})
        name = personal.get('name', 'resume').replace(' ', '_')
        output_file = self.output_dir / f"{name}_resume.pdf"
        
        # Create PDF document with configurable margins
        margin = self.config['margin']
        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=letter,
            rightMargin=margin*inch,
            leftMargin=margin*inch,
            topMargin=margin*inch,
            bottomMargin=margin*inch
        )
        
        # Build header (always first)
        self._build_header()
        
        # Map section names to their build methods
        section_builders = {
            'summary': self._build_summary,
            'experience': self._build_experience,
            'education': self._build_education,
            'skills': self._build_skills,
            'projects': self._build_projects,
            'certifications': self._build_certifications,
            'awards': self._build_awards,
            'publications': self._build_publications,
            'languages': self._build_languages,
            'volunteer': self._build_volunteer
        }
        
        # Build sections in configured order
        for section_name in self.config['section_order']:
            if section_name in section_builders:
                section_builders[section_name]()
            else:
                print(f"Warning: Unknown section '{section_name}' in section_order config")
        
        # Add footer if configured (always last)
        if self.config['footer']:
            self.story.append(Spacer(1, 0.2*inch))
            footer_text = "Generated by Resume Generator | George Yuanji Wang"
            self.story.append(Paragraph(footer_text, self.styles['Footer']))
        
        # Build the PDF
        try:
            doc.build(self.story)
            print(f"✓ Resume generated successfully: {output_file}")
            return output_file
        except Exception as e:
            print(f"Error generating PDF: {e}")
            sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python resume_generator.py <yaml_file>")
        print("\nExample:")
        print("  python resume_generator.py resume.yaml")
        sys.exit(1)
    
    yaml_file = sys.argv[1]
    
    print(f"Loading resume data from: {yaml_file}")
    generator = ResumeGenerator(yaml_file)
    
    print("Generating PDF resume...")
    output_file = generator.generate()
    
    print(f"\n{'='*60}")
    print(f"Resume successfully created!")
    print(f"Output: {output_file}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()