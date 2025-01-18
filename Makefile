run-app:
	cd app && LOCAL=true npm run dev

run-db:
	cd supabase && supabase start
