"""
Management command to seed page templates.
Run with: python manage.py seed_templates
"""
from django.core.management.base import BaseCommand
from apps.pages.models import PageTemplate


class Command(BaseCommand):
    help = 'Seed page templates into the database'

    def handle(self, *args, **options):
        templates = [
            {
                'name': 'Fitness Pro',
                'slug': 'fitness-pro',
                'description': 'Bold hero section, services grid, testimonials, and strong CTAs',
                'category': 'fitness',
                'is_premium': False,
                'available_for_plans': ['free', 'pro', 'business'],
                'template_data': {
                    'sections': [
                        {
                            'type': 'hero',
                            'order': 0,
                            'content': {
                                'title': 'Transform Your Fitness',
                                'subtitle': 'Professional Training Solutions',
                                'cta_text': 'Get Started',
                                'background_image': None,
                                'overlay_opacity': 0.5
                            }
                        },
                        {
                            'type': 'services',
                            'order': 1,
                            'content': {
                                'title': 'Our Services',
                                'services': []
                            }
                        },
                        {
                            'type': 'testimonials',
                            'order': 2,
                            'content': {
                                'title': 'What Our Clients Say',
                                'testimonials': []
                            }
                        }
                    ],
                    'styles': {
                        'primary_color': '#3b82f6',
                        'font_family': 'Inter'
                    }
                }
            },
            {
                'name': 'Wellness Center',
                'slug': 'wellness-center',
                'description': 'Soft colors, about section, pricing cards, and contact form',
                'category': 'wellness',
                'is_premium': False,
                'available_for_plans': ['free', 'pro', 'business'],
                'template_data': {
                    'sections': [
                        {'type': 'hero', 'order': 0, 'content': {'title': 'Your Wellness Journey Starts Here'}},
                        {'type': 'about', 'order': 1, 'content': {'heading': 'About Us', 'content': ''}},
                        {'type': 'pricing', 'order': 2, 'content': {'title': 'Our Plans'}},
                        {'type': 'contact', 'order': 3, 'content': {'title': 'Get In Touch'}}
                    ],
                    'styles': {'primary_color': '#10b981', 'font_family': 'Inter'}
                }
            },
            {
                'name': 'Personal Trainer',
                'slug': 'personal-trainer',
                'description': 'Hero with trainer photo, packages, and booking CTA',
                'category': 'fitness',
                'is_premium': False,
                'available_for_plans': ['free', 'pro', 'business'],
                'template_data': {
                    'sections': [
                        {'type': 'hero', 'order': 0, 'content': {'title': 'Personal Training Excellence'}},
                        {'type': 'pricing', 'order': 1, 'content': {'title': 'Training Packages'}},
                        {'type': 'booking', 'order': 2, 'content': {'title': 'Book Your Session'}}
                    ],
                    'styles': {'primary_color': '#f59e0b', 'font_family': 'Inter'}
                }
            },
            {
                'name': 'Yoga Studio',
                'slug': 'yoga-studio',
                'description': 'Calming design, class schedule, gallery, and FAQ',
                'category': 'wellness',
                'is_premium': True,
                'available_for_plans': ['pro', 'business'],
                'template_data': {
                    'sections': [
                        {'type': 'hero', 'order': 0, 'content': {'title': 'Find Your Inner Peace'}},
                        {'type': 'services', 'order': 1, 'content': {'title': 'Class Schedule'}},
                        {'type': 'gallery', 'order': 2, 'content': {'title': 'Our Studio'}},
                        {'type': 'faq', 'order': 3, 'content': {'title': 'Frequently Asked Questions'}}
                    ],
                    'styles': {'primary_color': '#8b5cf6', 'font_family': 'Inter'}
                }
            },
            {
                'name': 'Nutrition Coach',
                'slug': 'nutrition-coach',
                'description': 'Clean layout, program cards, testimonials, and contact',
                'category': 'nutrition',
                'is_premium': False,
                'available_for_plans': ['free', 'pro', 'business'],
                'template_data': {
                    'sections': [
                        {'type': 'hero', 'order': 0, 'content': {'title': 'Transform Your Health'}},
                        {'type': 'services', 'order': 1, 'content': {'title': 'Nutrition Programs'}},
                        {'type': 'testimonials', 'order': 2, 'content': {'title': 'Success Stories'}},
                        {'type': 'contact', 'order': 3, 'content': {'title': 'Start Your Journey'}}
                    ],
                    'styles': {'primary_color': '#06b6d4', 'font_family': 'Inter'}
                }
            },
            {
                'name': 'CrossFit Box',
                'slug': 'crossfit-box',
                'description': 'Energetic design, membership tiers, gallery, and social proof',
                'category': 'fitness',
                'is_premium': True,
                'available_for_plans': ['pro', 'business'],
                'template_data': {
                    'sections': [
                        {'type': 'hero', 'order': 0, 'content': {'title': 'Push Your Limits'}},
                        {'type': 'pricing', 'order': 1, 'content': {'title': 'Membership Tiers'}},
                        {'type': 'gallery', 'order': 2, 'content': {'title': 'Our Box'}},
                        {'type': 'testimonials', 'order': 3, 'content': {'title': 'Member Stories'}}
                    ],
                    'styles': {'primary_color': '#ef4444', 'font_family': 'Inter'}
                }
            },
            {
                'name': 'Online Coaching',
                'slug': 'online-coaching',
                'description': 'Modern layout, virtual services, pricing, and testimonials',
                'category': 'general',
                'is_premium': False,
                'available_for_plans': ['free', 'pro', 'business'],
                'template_data': {
                    'sections': [
                        {'type': 'hero', 'order': 0, 'content': {'title': 'Coaching From Anywhere'}},
                        {'type': 'services', 'order': 1, 'content': {'title': 'Virtual Services'}},
                        {'type': 'pricing', 'order': 2, 'content': {'title': 'Coaching Plans'}},
                        {'type': 'testimonials', 'order': 3, 'content': {'title': 'Client Results'}}
                    ],
                    'styles': {'primary_color': '#6366f1', 'font_family': 'Inter'}
                }
            },
            {
                'name': 'Bootcamp',
                'slug': 'bootcamp',
                'description': 'High-energy hero, program details, before/after gallery',
                'category': 'fitness',
                'is_premium': True,
                'available_for_plans': ['pro', 'business'],
                'template_data': {
                    'sections': [
                        {'type': 'hero', 'order': 0, 'content': {'title': 'Intensive Training Programs'}},
                        {'type': 'services', 'order': 1, 'content': {'title': 'Bootcamp Programs'}},
                        {'type': 'gallery', 'order': 2, 'content': {'title': 'Before & After'}},
                        {'type': 'contact', 'order': 3, 'content': {'title': 'Join Now'}}
                    ],
                    'styles': {'primary_color': '#dc2626', 'font_family': 'Inter'}
                }
            },
            {
                'name': 'Senior Fitness',
                'slug': 'senior-fitness',
                'description': 'Accessible design, gentle services, testimonials, and contact',
                'category': 'fitness',
                'is_premium': False,
                'available_for_plans': ['free', 'pro', 'business'],
                'template_data': {
                    'sections': [
                        {'type': 'hero', 'order': 0, 'content': {'title': 'Stay Active, Stay Strong'}},
                        {'type': 'services', 'order': 1, 'content': {'title': 'Gentle Fitness Programs'}},
                        {'type': 'testimonials', 'order': 2, 'content': {'title': 'Member Testimonials'}},
                        {'type': 'contact', 'order': 3, 'content': {'title': 'Get Started'}}
                    ],
                    'styles': {'primary_color': '#059669', 'font_family': 'Inter'}
                }
            },
            {
                'name': 'Athletic Performance',
                'slug': 'athletic-performance',
                'description': 'Professional layout, services, results, and booking',
                'category': 'fitness',
                'is_premium': True,
                'available_for_plans': ['pro', 'business'],
                'template_data': {
                    'sections': [
                        {'type': 'hero', 'order': 0, 'content': {'title': 'Elite Performance Training'}},
                        {'type': 'services', 'order': 1, 'content': {'title': 'Training Services'}},
                        {'type': 'about', 'order': 2, 'content': {'heading': 'Our Approach'}},
                        {'type': 'booking', 'order': 3, 'content': {'title': 'Schedule Consultation'}}
                    ],
                    'styles': {'primary_color': '#1e40af', 'font_family': 'Inter'}
                }
            },
        ]

        created_count = 0
        updated_count = 0

        for template_data in templates:
            template, created = PageTemplate.objects.update_or_create(
                slug=template_data['slug'],
                defaults={
                    'name': template_data['name'],
                    'description': template_data['description'],
                    'category': template_data['category'],
                    'is_premium': template_data['is_premium'],
                    'available_for_plans': template_data['available_for_plans'],
                    'template_data': template_data['template_data'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created template: {template.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Updated template: {template.name}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully seeded templates: {created_count} created, {updated_count} updated'
            )
        )

