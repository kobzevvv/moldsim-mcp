import { findMaterial, listMaterials } from './materials.js';

describe('findMaterial', () => {
  describe('exact ID match', () => {
    test('pc → Polycarbonate (not PP Copolymer)', () => {
      const results = findMaterial('pc');
      expect(results[0].id).toBe('pc');
      expect(results[0].name).toContain('Polycarbonate');
    });

    test('pa66-gf30 → PA66-GF30 (not PA6 or PA66)', () => {
      const results = findMaterial('pa66-gf30');
      expect(results[0].id).toBe('pa66-gf30');
    });

    test('abs-generic → ABS Generic', () => {
      const results = findMaterial('abs-generic');
      expect(results[0].id).toBe('abs-generic');
    });

    test('pa6 → PA6 Nylon 6 first', () => {
      const results = findMaterial('pa6');
      expect(results[0].id).toBe('pa6');
    });

    test('pom → POM Acetal', () => {
      const results = findMaterial('pom');
      expect(results[0].id).toBe('pom');
    });
  });

  describe('fuzzy match', () => {
    test('ABS (uppercase) finds abs-generic', () => {
      const results = findMaterial('ABS');
      expect(results.some(m => m.id === 'abs-generic')).toBe(true);
    });

    test('PA (family) finds all PA materials', () => {
      const results = findMaterial('PA');
      const ids = results.map(m => m.id);
      expect(ids).toContain('pa6');
      expect(ids).toContain('pa66');
      expect(ids).toContain('pa66-gf30');
    });

    test('PA66 finds pa66 and pa66-gf30 (starts-with)', () => {
      const results = findMaterial('PA66');
      const ids = results.map(m => m.id);
      expect(ids).toContain('pa66');
      expect(ids).toContain('pa66-gf30');
      // pa66 should rank above pa66-gf30 (exact match)
      expect(ids.indexOf('pa66')).toBeLessThan(ids.indexOf('pa66-gf30'));
    });
  });

  describe('edge cases', () => {
    test('empty string returns empty array', () => {
      expect(findMaterial('')).toHaveLength(0);
    });

    test('unknown material returns empty array', () => {
      expect(findMaterial('doesnotexist12345')).toHaveLength(0);
    });

    test('no false positives from empty filler field', () => {
      // regression: empty filler was matching every query via q.includes("")
      const results = findMaterial('xyz_no_match');
      expect(results).toHaveLength(0);
    });

    test('pc does not rank pp-copo first', () => {
      const results = findMaterial('pc');
      expect(results[0].id).not.toBe('pp-copo');
    });
  });
});

describe('listMaterials', () => {
  test('returns 21 materials', () => {
    expect(listMaterials()).toHaveLength(21);
  });

  test('each entry has id, name, family', () => {
    for (const m of listMaterials()) {
      expect(m.id).toBeTruthy();
      expect(m.name).toBeTruthy();
      expect(m.family).toBeTruthy();
    }
  });
});
