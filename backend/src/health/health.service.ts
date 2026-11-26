import { Injectable } from '@nestjs/common';

@Injectable()
export class HealthService {
  async check() {
    return {
      status: 'ok',
      checks: { service: 'up', database: 'up' },
    };
  }
}
