"""Adds the NIV entries (030-071) to verses.json. Run once from the repo root.

Every NIV verse here was typed from the NIV (2011) and must be confirmed word for word
against the published text (see docs/niv-checklist.md) before wide sharing.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PATH = os.path.join(ROOT, 'app', 'src', 'main', 'assets', 'content', 'verses.json')

# (id, layout, categories, theme, reference, verse, reflection, prayer)
NIV = [
 ('030', 'bottom', ['Faith', 'Hope'], 'Promise', 'Genesis 9:13',
  'I have set my rainbow in the clouds, and it will be the sign of the covenant between me and the earth.',
  'Every rainbow is a reminder that God keeps His promises. What He has said, He will do.',
  'Faithful God, thank You for keeping every promise You make. When I doubt, remind me that Your word never fails. Amen.'),
 ('031', 'top', ['Worship', 'Faith'], 'Holiness', 'Exodus 3:5',
  '‘Do not come any closer,’ God said. ‘Take off your sandals, for the place where you are standing is holy ground.’',
  'God meets us in ordinary places and makes them holy. Slow down today and notice that He is near.',
  'Holy God, teach me to approach You with reverence and wonder. Make my ordinary day a place where I meet You. Amen.'),
 ('032', 'top', ['Strength', 'Peace'], 'Deliverance', 'Exodus 14:14',
  'The LORD will fight for you; you need only to be still.',
  'Some battles are not yours to fight. Stand still, trust God, and watch Him make a way where there was none.',
  'Lord, I give You the battles I cannot win on my own. Fight for me, and help me to be still and trust You. Amen.'),
 ('033', 'bottom', ['Bible', "God's Love"], 'Devotion', 'Deuteronomy 6:5',
  'Love the LORD your God with all your heart and with all your soul and with all your strength.',
  'God does not ask for part of your heart. He invites all of you, and He gives all of Himself in return.',
  'Lord, I want to love You with everything I am. Take my heart, my soul and my strength, and make them Yours. Amen.'),
 ('034', 'bottom', ['Faith', 'Hope'], 'Presence', 'Genesis 28:15',
  'I am with you and will watch over you wherever you go, and I will bring you back to this land. I will not leave you until I have done what I have promised you.',
  'Even when you feel far from home, God is with you. He will finish what He has started in your life.',
  'Father, thank You for watching over me wherever I go. I trust You to complete what You have promised. Amen.'),
 ('035', 'top', ['Worship', 'Strength'], 'Praise', 'Psalm 28:7',
  'The LORD is my strength and my shield; my heart trusts in him, and he helps me. My heart leaps for joy, and with my song I praise him.',
  'Like David with his harp, let your trust in God turn into a song. Praise is the natural sound of a trusting heart.',
  'Lord, You are my strength and my shield. My heart trusts in You, and today I will praise You with joy. Amen.'),
 ('036', 'top', ['Peace', 'Faith'], 'Stillness', '1 Kings 19:12',
  'After the earthquake came a fire, but the LORD was not in the fire. And after the fire came a gentle whisper.',
  'God is not always in the loud and dramatic. Make room for quiet today, and listen for His gentle whisper.',
  'Lord, quiet the noise around me and within me. Help me to hear Your gentle whisper today. Amen.'),
 ('037', 'top', ['Faith', 'Peace'], 'Protection', 'Psalm 125:2',
  'As the mountains surround Jerusalem, so the LORD surrounds his people both now and forevermore.',
  'You are surrounded, not by trouble, but by the Lord Himself. He is around you on every side.',
  'Lord, surround me and my family with Your presence today, as the mountains surround Jerusalem. Amen.'),
 ('038', 'center', ['Jesus', 'Hope'], 'Christmas', 'Isaiah 9:6',
  'For to us a child is born, to us a son is given, and the government will be on his shoulders. And he will be called Wonderful Counselor, Mighty God, Everlasting Father, Prince of Peace.',
  'The child of Bethlehem carries the weight of the world on His shoulders, so you do not have to carry it on yours.',
  'Jesus, Wonderful Counselor and Prince of Peace, rule in my heart today. I rest my burdens on Your shoulders. Amen.'),
 ('039', 'center', ['Jesus', 'Hope'], 'Good News', 'Luke 2:10',
  'But the angel said to them, ‘Do not be afraid. I bring you good news that will cause great joy for all the people.’',
  'The first words of the Christmas message were “Do not be afraid.” The good news is still for you today.',
  'Lord, replace my fear with the joy of the good news. Help me to share that joy with someone today. Amen.'),
 ('040', 'center', ['Jesus', 'Worship'], 'Joy', 'Matthew 2:10',
  'When they saw the star, they were overjoyed.',
  'The wise men travelled far to find Jesus, and the journey ended in joy. Keep seeking Him; He is worth it.',
  'Lord Jesus, I want to seek You like the wise men did. Lead me to You, and fill my heart with joy. Amen.'),
 ('041', 'bottom', ['Jesus', "God's Love"], 'Beloved', 'Matthew 3:17',
  'And a voice from heaven said, ‘This is my Son, whom I love; with him I am well pleased.’',
  'In Christ, you are also a beloved child of God. Let His voice, not the world’s, tell you who you are.',
  'Father, thank You that in Jesus I am Your beloved child. Help me to live today from Your love. Amen.'),
 ('042', 'bottom', ['Jesus', 'Faith'], 'Calling', 'Matthew 4:19',
  '‘Come, follow me,’ Jesus said, ‘and I will send you out to fish for people.’',
  'Jesus still calls ordinary people to follow Him. You don’t need to be ready; you only need to say yes.',
  'Jesus, I will follow You. Use my ordinary life to draw others to You. Amen.'),
 ('043', 'top', ['Jesus', 'Strength'], 'Courage', 'Matthew 14:27',
  'But Jesus immediately said to them: ‘Take courage! It is I. Don’t be afraid.’',
  'In the middle of the storm, Jesus comes walking toward you. His presence is your courage.',
  'Jesus, when the winds are strong around me, let me hear You say, “It is I.” Give me courage today. Amen.'),
 ('044', 'top', ['Jesus', 'Gratitude'], 'Provision', 'John 6:35',
  'Then Jesus declared, ‘I am the bread of life. Whoever comes to me will never go hungry, and whoever believes in me will never be thirsty.’',
  'The deepest hunger of your heart is not for more things but for Jesus. Come to Him and be satisfied.',
  'Jesus, You are the bread of life. Satisfy my heart today, and teach me to come to You first. Amen.'),
 ('045', 'top', ['Jesus', 'Faith'], 'Surrender', 'Luke 22:42',
  '‘Father, if you are willing, take this cup from me; yet not my will, but yours be done.’',
  'Jesus shows us that honest prayer and surrender belong together. Tell God what you feel, then trust His will.',
  'Father, here is what I want, and here is my heart. Yet not my will, but Yours be done. Amen.'),
 ('046', 'bottom', ['Cross', "God's Love"], 'Grace', 'Romans 5:8',
  'But God demonstrates his own love for us in this: While we were still sinners, Christ died for us.',
  'God did not wait for you to be good enough. He loved you at your worst and gave His Son for you.',
  'Thank You, Jesus, for dying for me while I was still a sinner. Help me to rest in Your amazing love. Amen.'),
 ('047', 'top', ['Jesus', 'Hope', 'Cross'], 'Resurrection', 'Matthew 28:6',
  'He is not here; he has risen, just as he said. Come and see the place where he lay.',
  'The tomb is empty. Because Jesus lives, death does not have the final word over your life.',
  'Risen Lord, thank You for defeating death. Fill me with living hope today. Amen.'),
 ('048', 'top', ['Jesus', 'Bible'], 'Presence', 'Luke 24:32',
  'They asked each other, ‘Were not our hearts burning within us while he talked with us on the road and opened the Scriptures to us?’',
  'Jesus often walks beside us before we recognise Him. Open the Scriptures today and let Him warm your heart.',
  'Lord Jesus, walk with me today and open the Scriptures to me. Let my heart burn with love for You. Amen.'),
 ('049', 'top', ['Jesus', 'Cross'], 'Communion', '1 Corinthians 11:26',
  'For whenever you eat this bread and drink this cup, you proclaim the Lord’s death until he comes.',
  'Every time we remember the bread and the cup, we proclaim the greatest love story ever told.',
  'Lord Jesus, thank You for Your body broken and Your blood poured out for me. I remember You today. Amen.'),
 ('050', 'top', ['Jesus', 'Faith'], 'Abiding', 'John 15:5',
  'I am the vine; you are the branches. If you remain in me and I in you, you will bear much fruit; apart from me you can do nothing.',
  'Fruit is not forced; it grows from staying connected. Stay close to Jesus today, and let Him grow good things in you.',
  'Jesus, You are the vine and I am a branch. Keep me close to You, and let my life bear good fruit. Amen.'),
 ('051', 'center', ['Peace', 'Nature & Creation'], 'Trust', 'Matthew 6:34',
  'Therefore do not worry about tomorrow, for tomorrow will worry about itself. Each day has enough trouble of its own.',
  'God gives grace for today, not for every tomorrow at once. Live this day with Him, one step at a time.',
  'Father, I give You my worries about tomorrow. Help me to live today with trust and peace. Amen.'),
 ('052', 'top', ['Faith', 'Bible'], 'Light', 'Matthew 5:16',
  'In the same way, let your light shine before others, that they may see your good deeds and glorify your Father in heaven.',
  'Small acts of kindness are like a lamp in a dark room. Let your light shine today so others see God’s goodness.',
  'Lord, let my life shine for You today. May my words and deeds point others to Your goodness. Amen.'),
 ('053', 'top', ['Jesus', 'Cross'], 'Lamb of God', 'John 1:29',
  'The next day John saw Jesus coming toward him and said, ‘Look, the Lamb of God, who takes away the sin of the world!’',
  'Jesus is the Lamb of God who carries away what you could never carry. Look to Him and be free.',
  'Lamb of God, thank You for taking away my sin. Help me to walk today in Your freedom. Amen.'),
 ('054', 'top', ['Faith', 'Strength'], 'Holy Spirit', 'Acts 1:8',
  'But you will receive power when the Holy Spirit comes on you; and you will be my witnesses in Jerusalem, and in all Judea and Samaria, and to the ends of the earth.',
  'You are not sent out in your own strength. The Holy Spirit gives power to ordinary people to share extraordinary news.',
  'Holy Spirit, fill me with Your power today. Make me a faithful witness wherever I go. Amen.'),
 ('055', 'top', ["God's Love", 'Family'], 'Homecoming', 'Luke 15:20',
  'So he got up and went to his father. But while he was still a long way off, his father saw him and was filled with compassion for him; he ran to his son, threw his arms around him and kissed him.',
  'However far you have wandered, the Father is watching the road for you. He runs to meet you with open arms.',
  'Father, thank You for running to meet me with compassion. I come home to You today. Amen.'),
 ('056', 'top', ['Psalm 23', 'Strength'], 'Comfort', 'Psalm 23:4',
  'Even though I walk through the darkest valley, I will fear no evil, for you are with me; your rod and your staff, they comfort me.',
  'The valley is real, but so is the Shepherd. You are not walking through it alone.',
  'Lord, when I walk through dark valleys, let me feel Your presence. Comfort me and lead me through. Amen.'),
 ('057', 'bottom', ['Psalm 23', "God's Love"], 'Goodness', 'Psalm 23:6',
  'Surely your goodness and love will follow me all the days of my life, and I will dwell in the house of the LORD forever.',
  'God’s goodness and love are not behind you only on good days. They follow you all the days of your life.',
  'Lord, thank You that Your goodness and love follow me every day. Help me to notice them today. Amen.'),
 ('058', 'top', ['Faith', 'Peace'], 'Refuge', 'Psalm 91:4',
  'He will cover you with his feathers, and under his wings you will find refuge; his faithfulness will be your shield and rampart.',
  'Like a bird sheltering her young, God gathers you close. You can rest under His wings today.',
  'Lord, cover me with Your wings and be my refuge. I trust in Your faithfulness. Amen.'),
 ('059', 'bottom', ['Peace'], 'Perfect Peace', 'Isaiah 26:3',
  'You will keep in perfect peace those whose minds are steadfast, because they trust in you.',
  'Peace grows where the mind rests on God. Set your thoughts on Him today, again and again.',
  'Lord, keep my mind steadfast on You, and fill me with Your perfect peace. Amen.'),
 ('060', 'top', ['Peace', 'Faith'], 'Prayer', 'Philippians 4:6',
  'Do not be anxious about anything, but in every situation, by prayer and petition, with thanksgiving, present your requests to God.',
  'Turn every worry into a prayer. Bring it to God with thanks, and let Him carry it.',
  'Father, I bring You my requests with a thankful heart. Take my anxiety and give me Your peace. Amen.'),
 ('061', 'top', ['Hope', 'Faith'], 'Purpose', 'Romans 8:28',
  'And we know that in all things God works for the good of those who love him, who have been called according to his purpose.',
  'Like a river finding its way through a valley, God is working through every bend of your story.',
  'Lord, I trust that You are working all things for good. Help me to love You and follow Your purpose. Amen.'),
 ('062', 'bottom', ['Hope', 'Nature & Creation'], 'New Life', '2 Corinthians 5:17',
  'Therefore, if anyone is in Christ, the new creation has come: The old has gone, the new is here!',
  'In Christ, spring has come to your soul. The old has gone; you can begin again today.',
  'Lord, thank You for making me new in Christ. Help me to leave the old behind and walk in new life. Amen.'),
 ('063', 'bottom', ['Cross', "God's Love"], 'Grace', 'Ephesians 2:8–9',
  'For it is by grace you have been saved, through faith—and this is not from yourselves, it is the gift of God—not by works, so that no one can boast.',
  'Salvation is a gift, not a wage. You can stop trying to earn God’s love and simply receive it.',
  'Lord, thank You for the gift of grace. I receive it with open hands and a grateful heart. Amen.'),
 ('064', 'bottom', ['Strength', 'Faith'], 'Light', 'Psalm 27:1',
  'The LORD is my light and my salvation—whom shall I fear? The LORD is the stronghold of my life—of whom shall I be afraid?',
  'When the night feels long, the Lord is your light. When the storm is strong, He is your stronghold.',
  'Lord, You are my light and my salvation. Drive away my fear and be my stronghold today. Amen.'),
 ('065', 'center', ['Faith', 'Gratitude'], 'Delight', 'Psalm 37:4',
  'Take delight in the LORD, and he will give you the desires of your heart.',
  'As you delight in God, He shapes the desires of your heart to match His good plans.',
  'Lord, help me to delight in You above everything else. Shape the desires of my heart. Amen.'),
 ('066', 'top', ['Marriage', "God's Love"], 'Love', 'Colossians 3:14',
  'And over all these virtues put on love, which binds them all together in perfect unity.',
  'Love is what holds everything else together. Put it on today like a garment, at home first.',
  'Lord, clothe me with love today. Bind my marriage and my relationships together in perfect unity. Amen.'),
 ('067', 'top', ['Family', 'Gratitude'], 'Children', 'Psalm 127:3',
  'Children are a heritage from the LORD, offspring a reward from him.',
  'Every child is a gift entrusted by God. Thank Him today for the children in your life.',
  'Father, thank You for the children You have placed in my life. Help me to love, guide and pray for them. Amen.'),
 ('068', 'top', ['Gratitude', 'Worship'], 'Thanksgiving', 'Psalm 100:4',
  'Enter his gates with thanksgiving and his courts with praise; give thanks to him and praise his name.',
  'Thanksgiving is the gate into God’s presence. Begin your prayers today with thank You.',
  'Lord, I enter Your presence with thanksgiving. Thank You for Your goodness and Your faithful love. Amen.'),
 ('069', 'center', ['Hope', "God's Love"], 'Comfort', 'Psalm 34:18',
  'The LORD is close to the brokenhearted and saves those who are crushed in spirit.',
  'If your heart is heavy today, God is not far away. He draws closest when you are hurting most.',
  'Lord, You are close to the brokenhearted. Draw near to me and to those I love who are hurting. Amen.'),
 ('070', 'top', ['Jesus', 'Hope'], 'Light of the World', 'John 8:12',
  'When Jesus spoke again to the people, he said, ‘I am the light of the world. Whoever follows me will never walk in darkness, but will have the light of life.’',
  'You don’t need to see the whole path. Follow Jesus, and you will always have enough light for the next step.',
  'Jesus, light of the world, shine on my path today. Help me to follow You and never walk in darkness. Amen.'),
 ('071', 'top', ['Peace', "God's Love"], 'Care', '1 Peter 5:7',
  'Cast all your anxiety on him because he cares for you.',
  'You are not a burden to God. He cares for you, so you can hand Him everything that weighs on you.',
  'Lord, I cast all my anxiety on You, because You care for me. Thank You for holding what I cannot. Amen.'),
]

ANIMATED = {'001': 'pasture'}


def main():
    doc = json.load(open(PATH, encoding='utf-8'))
    doc['translations'] = {
        'KJV': {'name': 'King James Version', 'note': 'Public domain'},
        'NIV': {'name': 'New International Version', 'note': 'Scripture quotations marked NIV are taken from The Holy Bible, New International Version®, NIV®. Copyright © 1973, 1978, 1984, 2011 by Biblica, Inc.™ Used by permission. All rights reserved worldwide.'},
    }
    doc['translation']['note'] = 'Public domain. LORD is set in small capitals, as in printed Bibles.'
    entries = [e for e in doc['entries'] if int(e['id']) < 30]
    for e in entries:
        e['translation'] = 'KJV'
        if e['id'] in ANIMATED:
            e['animation'] = ANIMATED[e['id']]
    for i, (id_, layout, cats, theme, ref, verse, refl, prayer) in enumerate(NIV):
        for c in cats:
            assert c in doc['categories'], c
        entries.append({
            'id': id_, 'dateIndex': int(id_), 'image': f'wallpaper_{id_}.jpg', 'verse': verse, 'reference': ref,
            'translation': 'NIV', 'excerpt': False, 'theme': theme, 'categories': cats, 'reflection': refl,
            'prayer': prayer, 'layout': layout, 'artwork': 'painted',
        })
    # Alternate the two translations through the daily cycle, starting with Psalm 23:1 (KJV).
    kjv = [e for e in entries if e['translation'] == 'KJV']
    niv = [e for e in entries if e['translation'] == 'NIV']
    order = []
    while kjv or niv:
        if kjv:
            order.append(kjv.pop(0))
        if niv:
            order.append(niv.pop(0))
    for n, e in enumerate(order, 1):
        e['dateIndex'] = n
        e['artwork'] = 'painted'
    doc['entries'] = order
    json.dump(doc, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(len(entries), 'entries')


if __name__ == '__main__':
    main()
