create index if not exists idx_vehicle_photos_vehicle_created
  on public.vehicle_photos (vehicle_id, created_at);

create index if not exists idx_expenses_vehicle_created
  on public.expenses (vehicle_id, created_at);

create index if not exists idx_proposals_vehicle_created
  on public.proposals (vehicle_id, created_at);

create index if not exists idx_sales_vehicle_created
  on public.sales (vehicle_id, created_at);

create index if not exists idx_vehicles_created
  on public.vehicles (created_at desc);
