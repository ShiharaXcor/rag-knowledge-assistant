from vector_store import query_store

print("--- As 'employee' asking about salary ---")
results = query_store("What is the salary range for a Staff Engineer?", user_role="employee")
print(f"Results found: {len(results)}")
for r in results:
    print(f"  {r['source']}")

print("\n--- As 'hr' asking about salary ---")
results = query_store("What is the salary range for a Staff Engineer?", user_role="hr")
print(f"Results found: {len(results)}")
for r in results:
    print(f"  {r['source']}")