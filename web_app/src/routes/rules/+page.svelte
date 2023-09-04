<script lang="ts">
	import GameImg1 from '$lib/images/gameboard-1.png'
	import GameImg2 from '$lib/images/gameboard-2.png'
	import ForwardImg from '$lib/images/forward.png'
	import Forward2Img from '$lib/images/2forward.png'
	import LeftImg from '$lib/images/left.png'
	import RightImg from '$lib/images/right.png'
	import UturnImg from '$lib/images/uturn.png'

	let isSecondDay = false

	let today = new Date()
	try {
		const todayDate = today.toISOString().split('T')[0]
		isSecondDay = todayDate === '2023-09-07'
	} catch (e) {
		console.log(e)
	}
</script>

<div class="w-full flex justify-center py-10 pb-40 text-black">
	<section class="prose parch p-4 rounded-lg mx-2 z-10">
		<h1 class="pixel-font">Game Rules</h1>
		<p>Welcome to our Microbit and Bitbot game! Here are the rules to get you started:</p>

		<h2 class="pixel-font">Objective</h2>
		<p>
			The goal of the game is to drive the Bitbot car around the field and gather as many points as
			possible in three rounds.
		</p>

		<h2 class="pixel-font">How to Play</h2>
		<ol class="list-disc marker:text-black">
			<li>Register in the app on our client machine.</li>
			<li>You will get three rounds to play.</li>
			<li>
				When you are ready, draw 7 random cards. Each card represents a direction:
				<div class="grid md:grid-cols-2 items-center">
					<div class="flex items-center gap-2">
						<img alt="" class="w-28 rounded-lg border-4 border-blue-500" src={ForwardImg} />
						Forward until next intersection
					</div>
					<div class="flex items-center gap-2">
						<img alt="" class="w-28 rounded-lg border-4 border-blue-500" src={LeftImg} />
						Turn left and drive to next intersection
					</div>
					<div class="flex items-center gap-2">
						<img alt="" class="w-28 rounded-lg border-4 border-blue-500" src={RightImg} />
						Turn right and drive to next intersection
					</div>
					<div class="flex items-center gap-2">
						<img alt="" class="w-28 border-4 border-purple-500 rounded-lg" src={UturnImg} />
						<span>Take a u-turn and drive to next intersection <b>[rare]</b> </span>
					</div>
					<div class="flex items-center gap-2">
						<img alt="" class="w-28 rounded-lg border-4 border-orange-500" src={Forward2Img} />
						<span>
							Same as forward, but twice <b>[legendary]</b>
						</span>
					</div>
				</div>
			</li>
			<li>Place the cards on the board in the order you want the car to move.</li>
			<li>
				The car will move from the starting intersection to the next intersection based on the
				direction of the cards.
			</li>
		</ol>

		<h2 class="pixel-font">Scoring</h2>
		<p>
			At each intersection, the player will either get positive or negative points. In the middle of
			the board, surrounded by negative points, there is a 6 pointer that could significantly
			increase your final score.
		</p>

		<h2 class="pixel-font">Game Board</h2>
		<div>
			<p>
				The game board is a rectangular board with black lines painted over that form intersections
				or crosses at each place a line crosses. These are the places where points are stored, and
				the car can drive to and fro.
			</p>
			<img
				src={isSecondDay ? GameImg2 : GameImg1}
				alt="Overview of the game board with the layout and how many points are where"
				class="w-full"
			/>
		</div>

		<h2 class="pixel-font">Winning</h2>
		<p>The player with the highest score at the end of the three rounds is the winner.</p>

		<h2 class="pixel-font">Good Luck!</h2>
		<p>Now that you know the rules, you are ready to play. Good luck!</p>
	</section>
</div>
