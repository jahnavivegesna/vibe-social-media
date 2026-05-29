"""
VIBE - Demo Data Seeder
========================
Run: python manage.py seed_data

Creates demo users, posts, follows, likes, comments, and hashtags
so you can immediately see a populated VIBE feed.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from vibe_app.models import UserProfile, Post, Comment, Like, Follow, Hashtag
import random


DEMO_USERS = [
    {"username": "alex_vibes",    "first": "Alex",    "last": "Johnson", "bio": "🎸 Music lover | Coffee addict | Living my best life #vibes"},
    {"username": "sara_creates",  "first": "Sara",    "last": "Kim",     "bio": "🎨 Digital artist & photographer | She/Her | DMs open ✨"},
    {"username": "dev_mike",      "first": "Mike",    "last": "Torres",  "bio": "👨‍💻 Full-stack dev | Open source enthusiast | Building cool stuff"},
    {"username": "foodie_priya",  "first": "Priya",   "last": "Sharma",  "bio": "🍜 Food blogger | Recipes, restaurants & food adventures"},
    {"username": "travel_raj",    "first": "Raj",     "last": "Patel",   "bio": "✈️ Exploring 195 countries | Travel tips & hidden gems"},
    {"username": "fit_emma",      "first": "Emma",    "last": "Wilson",  "bio": "💪 Fitness coach | Healthy lifestyle advocate | Let's get moving!"},
    {"username": "tech_zara",     "first": "Zara",    "last": "Ahmed",   "bio": "🤖 AI researcher | Tech news | Future is now #technology"},
    {"username": "art_lucas",     "first": "Lucas",   "last": "Martin",  "bio": "🖌️ Artist & illustrator | Commissions open | Art is life"},
]

DEMO_POSTS = [
    {"content": "Just launched my new portfolio website! 🚀 Built with Django and a lot of coffee ☕ Check it out! #webdev #django #portfolio", "type": "text"},
    {"content": "Golden hour hit different today 🌅 Sometimes you just need to stop and appreciate the little moments. #photography #sunset #vibes", "type": "text"},
    {"content": "Made homemade ramen from scratch today! 🍜 Took 6 hours but absolutely worth it. The broth is everything! #food #cooking #ramen #foodie", "type": "text"},
    {"content": "3 months of consistent gym work and I'm finally seeing results! 💪 Consistency > Intensity every single time. #fitness #gym #motivation", "type": "text"},
    {"content": "Hot take: dark mode isn't just aesthetic, it actually helps me code better at night 🌙 Who else is a dark mode enjoyer? #coding #devlife", "type": "text"},
    {"content": "Explored a hidden waterfall in Bali today 🌊 No tourists, just pure nature. This is why I travel! #travel #bali #wanderlust #nature", "type": "text"},
    {"content": "New digital art piece done! ✨ Spent 12 hours on this one. What do you think? #digitalart #illustration #art #creative", "type": "text"},
    {"content": "AI just wrote 80% of my boilerplate code and I'm not mad about it 😅 The future is wild. #ai #programming #tech #future", "type": "text"},
    {"content": "Morning routine that changed my life: wake up 5am, meditate 10min, journal 15min, workout 45min. By 7am I've done more than most do all day 🌄 #productivity #morning #selfcare", "type": "text"},
    {"content": "Street food tour of Mumbai complete 🇮🇳 Vada pav, pav bhaji, bhel puri... my stomach is happy and so am I! #food #travel #india #streetfood", "type": "text"},
    {"content": "Finally finished reading 'Atomic Habits' 📚 The 1% better every day concept hit me hard. Tiny changes = massive results. #books #habits #selfimprovement", "type": "text"},
    {"content": "Built my first CLI tool today and deployed it to PyPI! 🐍 Open source is the best. #python #opensource #coding", "type": "text"},
    {"content": "Sunset from my balcony tonight 🌇 Reminder: you don't need to travel far to find beauty. #photography #sunset #home #grateful", "type": "text"},
    {"content": "Tried a new Mediterranean restaurant and oh my goodness 😩 The hummus alone was worth the trip! #food #mediterranean #foodie #restaurant", "type": "text"},
    {"content": "Started learning guitar 6 months ago. Today I played a full song without stopping! 🎸 Small wins matter. #music #guitar #learning #progress", "type": "text"},
    {"content": "The problem with social media is we compare our behind-the-scenes to everyone else's highlight reel. Be kind to yourself 💙 #mentalhealth #selfcare #mindfulness", "type": "text"},
    {"content": "New workout PR today! 🏋️ Squatted 100kg for the first time. The grind never lies! #fitness #powerlifting #gains #gym", "type": "text"},
    {"content": "Just got back from Tokyo 🇯🇵 Easily the most organized, clean, and beautiful city I've ever visited. Going back ASAP! #travel #tokyo #japan", "type": "text"},
    {"content": "Design tip: whitespace is not wasted space, it's breathing room for your content 🎨 More whitespace = better UX #design #ux #ui #webdesign", "type": "text"},
    {"content": "Cooked a full thanksgiving dinner for the first time at 24 🦃 It was chaotic, messy, and absolutely delicious. Adulting unlocked! #cooking #food #thanksgiving", "type": "text"},
]

DEMO_COMMENTS = [
    "This is absolutely amazing! 🔥",
    "Love this so much! Keep it up ✨",
    "You're so talented! Wow 😍",
    "Goals right here 💯",
    "This made my day! Thank you for sharing 🙏",
    "Incredible work as always! 👏",
    "Can't believe how good this is!",
    "Following for more content like this! 💫",
    "The quality is unreal 🤯",
    "This is exactly what I needed to see today ❤️",
    "How do you do it?? Teach me! 😅",
    "Actual inspiration right here 🌟",
    "This deserves way more attention!",
    "I'm obsessed 😍 so beautiful!",
    "Keep creating, you're amazing! 💪",
]


class Command(BaseCommand):
    help = 'Seeds VIBE with demo users, posts, follows, likes, and comments'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing demo data first')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🎯 VIBE Data Seeder Starting...\n'))

        if options['clear']:
            self.stdout.write('Clearing old demo data...')
            User.objects.filter(username__in=[u['username'] for u in DEMO_USERS]).delete()

        # ── Step 1: Create Users ──────────────────────────────────────
        created_users = []
        for data in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first'],
                    'last_name': data['last'],
                    'email': f"{data['username']}@vibedemo.com",
                }
            )
            if created:
                user.set_password('demo1234')
                user.save()
                # Update or create profile
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.bio = data['bio']
                profile.save()
                self.stdout.write(f"  ✅ Created user: @{user.username}")
            else:
                self.stdout.write(f"  ⏭️  Skipped (exists): @{user.username}")
            created_users.append(user)

        self.stdout.write(f'\n👥 {len(created_users)} users ready\n')

        # ── Step 2: Create Hashtags ──────────────────────────────────
        all_tags = [
            'vibes', 'coding', 'travel', 'food', 'art', 'photography',
            'fitness', 'music', 'technology', 'django', 'python', 'webdev',
            'motivation', 'lifestyle', 'nature', 'design', 'ai', 'creative',
            'foodie', 'wanderlust', 'gym', 'mindfulness', 'books', 'selfcare',
        ]
        hashtag_objs = {}
        for tag in all_tags:
            h, _ = Hashtag.objects.get_or_create(name=tag)
            hashtag_objs[tag] = h
        self.stdout.write(f'🏷️  {len(all_tags)} hashtags ready\n')

        # ── Step 3: Create Posts ──────────────────────────────────────
        created_posts = []
        for i, post_data in enumerate(DEMO_POSTS):
            author = created_users[i % len(created_users)]
            post, created = Post.objects.get_or_create(
                author=author,
                content=post_data['content'],
                defaults={'post_type': post_data['type']}
            )
            if created:
                # Extract and attach hashtags from content
                import re
                tags_in_content = re.findall(r'#(\w+)', post.content.lower())
                for tag_name in tags_in_content:
                    tag, _ = Hashtag.objects.get_or_create(name=tag_name)
                    post.hashtags.add(tag)
                self.stdout.write(f"  📝 Post by @{author.username}: {post.content[:50]}...")
            created_posts.append(post)

        self.stdout.write(f'\n📝 {len(created_posts)} posts ready\n')

        # ── Step 4: Create Follow Relationships ───────────────────────
        follow_count = 0
        for user in created_users:
            # Each user follows 3-6 random others
            others = [u for u in created_users if u != user]
            to_follow = random.sample(others, min(random.randint(3, 6), len(others)))
            for target in to_follow:
                follow, created = Follow.objects.get_or_create(
                    follower=user,
                    following=target
                )
                if created:
                    follow_count += 1

        self.stdout.write(f'👥 {follow_count} follow relationships created\n')

        # ── Step 5: Create Likes ──────────────────────────────────────
        like_count = 0
        for post in created_posts:
            # Random 2-7 users like each post
            likers = random.sample(created_users, min(random.randint(2, 7), len(created_users)))
            for liker in likers:
                if liker != post.author:
                    like, created = Like.objects.get_or_create(
                        user=liker,
                        post=post,
                        defaults={'is_active': True}
                    )
                    if created:
                        like_count += 1

        self.stdout.write(f'❤️  {like_count} likes created\n')

        # ── Step 6: Create Comments ───────────────────────────────────
        comment_count = 0
        for post in created_posts:
            # Random 1-4 comments per post
            commenters = random.sample(created_users, min(random.randint(1, 4), len(created_users)))
            for commenter in commenters:
                if commenter != post.author:
                    comment_text = random.choice(DEMO_COMMENTS)
                    comment, created = Comment.objects.get_or_create(
                        post=post,
                        author=commenter,
                        content=comment_text,
                    )
                    if created:
                        comment_count += 1

        self.stdout.write(f'💬 {comment_count} comments created\n')

        # ── Summary ───────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('🎉 VIBE Demo Data Seeded Successfully!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'   Users   : {User.objects.count()}')
        self.stdout.write(f'   Posts   : {Post.objects.filter(is_deleted=False).count()}')
        self.stdout.write(f'   Likes   : {Like.objects.filter(is_active=True).count()}')
        self.stdout.write(f'   Comments: {Comment.objects.filter(is_deleted=False).count()}')
        self.stdout.write(f'   Follows : {Follow.objects.count()}')
        self.stdout.write(f'   Hashtags: {Hashtag.objects.count()}')
        self.stdout.write(f'\n🔑 Login with any demo account:')
        self.stdout.write(f'   Username: alex_vibes  |  Password: demo1234')
        self.stdout.write(f'   Username: sara_creates |  Password: demo1234')
        self.stdout.write(f'\n🌐 Open: http://127.0.0.1:8000\n')
