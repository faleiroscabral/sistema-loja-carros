create extension if not exists "pgcrypto";

create table if not exists public.vehicles (
  id uuid primary key default gen_random_uuid(),
  brand text not null,
  model text not null,
  year integer not null,
  color text,
  mileage integer default 0,
  plate text,
  chassis text,
  purchase_price numeric(12, 2) default 0,
  sale_price numeric(12, 2) default 0,
  status text not null default 'Disponivel',
  notes text,
  created_at timestamptz not null default now()
);

create table if not exists public.vehicle_photos (
  id uuid primary key default gen_random_uuid(),
  vehicle_id uuid not null references public.vehicles(id) on delete cascade,
  photo_url text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.customers (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  phone text,
  email text,
  document text,
  notes text,
  created_at timestamptz not null default now()
);

create table if not exists public.proposals (
  id uuid primary key default gen_random_uuid(),
  vehicle_id uuid not null references public.vehicles(id) on delete cascade,
  customer_id uuid not null references public.customers(id) on delete cascade,
  proposed_price numeric(12, 2) default 0,
  payment_method text,
  status text not null default 'Aberta',
  notes text,
  created_at timestamptz not null default now()
);

create table if not exists public.sales (
  id uuid primary key default gen_random_uuid(),
  vehicle_id uuid not null references public.vehicles(id) on delete cascade,
  customer_id uuid not null references public.customers(id) on delete cascade,
  sale_price numeric(12, 2) default 0,
  sale_date date not null default current_date,
  notes text,
  created_at timestamptz not null default now()
);

create table if not exists public.expenses (
  id uuid primary key default gen_random_uuid(),
  vehicle_id uuid not null references public.vehicles(id) on delete cascade,
  description text not null,
  amount numeric(12, 2) default 0,
  expense_date date not null default current_date,
  created_at timestamptz not null default now()
);

alter table public.vehicles enable row level security;
alter table public.vehicle_photos enable row level security;
alter table public.customers enable row level security;
alter table public.proposals enable row level security;
alter table public.sales enable row level security;
alter table public.expenses enable row level security;

create policy "Temporary public access vehicles" on public.vehicles
  for all using (true) with check (true);
create policy "Temporary public access vehicle photos" on public.vehicle_photos
  for all using (true) with check (true);
create policy "Temporary public access customers" on public.customers
  for all using (true) with check (true);
create policy "Temporary public access proposals" on public.proposals
  for all using (true) with check (true);
create policy "Temporary public access sales" on public.sales
  for all using (true) with check (true);
create policy "Temporary public access expenses" on public.expenses
  for all using (true) with check (true);
