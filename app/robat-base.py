import aiohttp
import asyncio
from collections import defaultdict
import time
import json
from datetime import datetime

async def test_endpoint(session, url, request_id):
    start_time = time.time()
    headers = {"Authorization": "Basic token site"}
    try:
        async with session.get(url, headers=headers) as response:
            response_time = time.time() - start_time
            response_text = await response.text()
            return {
                'request_id': request_id,
                'status_code': response.status,
                'success': response.status == 200,
                'response_time': round(response_time, 3),
                'response_size': len(response_text),
                'timestamp': datetime.now().isoformat(),
                'headers': dict(response.headers)
            }
    except Exception as e:
        return {
            'request_id': request_id,
            'status_code': 0,
            'success': False,
            'error': str(e),
            'response_time': round(time.time() - start_time, 3),
            'timestamp': datetime.now().isoformat()
        }

async def run_batch_test(url, concurrent_requests, batch_id):
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(concurrent_requests):
            tasks.append(test_endpoint(session, url, i))
        
        results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    
    # تحلیل نتایج
    stats = {
        'batch_id': batch_id,
        'total_requests': concurrent_requests,
        'start_time': datetime.fromtimestamp(start_time).isoformat(),
        'end_time': datetime.fromtimestamp(end_time).isoformat(),
        'total_duration': round(end_time - start_time, 3),
        'successful_requests': sum(1 for r in results if r['success']),
        'failed_requests': sum(1 for r in results if not r['success']),
        'average_response_time': round(sum(r['response_time'] for r in results) / len(results), 3),
        'status_codes': defaultdict(int),
        'detailed_results': results
    }
    
    # محاسبه تعداد هر کد وضعیت
    for result in results:
        stats['status_codes'][str(result['status_code'])] += 1
    
    # محاسبه پرسنتایل‌های زمان پاسخ
    response_times = sorted(r['response_time'] for r in results)
    stats['response_time_percentiles'] = {
        'p50': round(response_times[len(response_times) // 2], 3),
        'p90': round(response_times[int(len(response_times) * 0.9)], 3),
        'p95': round(response_times[int(len(response_times) * 0.95)], 3),
        'p99': round(response_times[int(len(response_times) * 0.99)], 3)
    }
    
    return stats

async def main():
    url = 'site addrass'
    batch_sizes = [10, 20, 50, 100]
    
    final_report = {
        'test_url': url,
        'test_start_time': datetime.now().isoformat(),
        'test_configuration': {
            'batch_sizes': batch_sizes,
            'total_requests': sum(batch_sizes)
        },
        'batch_results': []
    }
    
    for i, batch_size in enumerate(batch_sizes):
        print(f"Running batch test {i+1} with {batch_size} concurrent requests...")
        results = await run_batch_test(url, batch_size, i+1)
        final_report['batch_results'].append(results)
        
    final_report['test_end_time'] = datetime.now().isoformat()
    
    # Calculate overall statistics
    final_report['overall_statistics'] = {
        'total_requests': sum(r['total_requests'] for r in final_report['batch_results']),
        'total_successful': sum(r['successful_requests'] for r in final_report['batch_results']),
        'total_failed': sum(r['failed_requests'] for r in final_report['batch_results']),
        'average_success_rate': round(
            sum(r['successful_requests'] for r in final_report['batch_results']) /
            sum(r['total_requests'] for r in final_report['batch_results']) * 100, 2
        ),
        'total_duration': round(sum(r['total_duration'] for r in final_report['batch_results']), 3)
    }
    
    # Save to file
    filename = f"stress_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)
    
    print(f"\nComplete report saved to file {filename}")
    
    # Display summary results
    print("\nSummary Results:")
    print("-" * 50)
    for batch in final_report['batch_results']:
        print(f"\nBatch {batch['batch_id']} ({batch['total_requests']} requests):")
        print(f"- Successful requests: {batch['successful_requests']}")
        print(f"- Failed requests: {batch['failed_requests']}")
        print(f"- Average response time: {batch['average_response_time']} seconds")
        print(f"- Status codes: {dict(batch['status_codes'])}")
        print(f"- 95th percentile response time: {batch['response_time_percentiles']['p95']} seconds")

if __name__ == "__main__":
    asyncio.run(main())
