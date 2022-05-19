/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class MetricService {

    /**
     * Get All Metrics
     * @param start
     * @param end
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getAllMetrics(
        start?: string,
        end?: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/metric/',
            query: {
                'start': start,
                'end': end,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Billing
     * @param account
     * @param start
     * @param end
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getBilling(
        account: number,
        start?: string,
        end?: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/metric/{account}',
            path: {
                'account': account,
            },
            query: {
                'start': start,
                'end': end,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}